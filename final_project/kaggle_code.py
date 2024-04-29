!pip install feature_engine==1.6.2
!pip install duckdb==0.9.2

import numpy as np
from scipy import stats
import pandas as pd
rng = np.random.default_rng(seed=12345)
np.set_printoptions(suppress=True, precision=4)
pd.options.display.float_format = '{:,.4f}'.format
pd.options.mode.copy_on_write = True
pd.options.future.infer_string = True
pd.options.future.no_silent_downcasting = True

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")

from feature_engine.selection import DropFeatures
from feature_engine.outliers import ArbitraryOutlierCapper
from feature_engine.imputation import (
        MeanMedianImputer,
        CategoricalImputer,
        AddMissingIndicator,
        ArbitraryNumberImputer
)
from feature_engine.encoding import (
        MeanEncoder,
        OrdinalEncoder,
        RareLabelEncoder
)

from sklearn.model_selection import (
        cross_val_score, 
        KFold
)
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

from xgboost import XGBClassifier

import os
import sys
import json
import duckdb

if '/kaggle/input/home-credit-support-files' not in sys.path:
    sys.path.insert(0, '/kaggle/input/home-credit-support-files')
import utils


def post_query_process(df):
    col_list = df.columns

    df = df.replace({-99999:np.NaN})

    if 'HOUR_APPR_PROCESS_START' in col_list:
        df['HOUR_APPR_PROCESS_START'] = df['HOUR_APPR_PROCESS_START'].astype('object')

    if 'FLAG_OWN_CAR' in col_list:
        df['FLAG_OWN_CAR'] = df['FLAG_OWN_CAR'].astype('object').replace({'Y':1, 'N':0}).astype('int')

    if 'FLAG_OWN_REALTY' in col_list:
        df['FLAG_OWN_REALTY'] = df['FLAG_OWN_REALTY'].astype('object').replace({'Y':1, 'N':0}).astype('int')

    if 'DAYS_BIRTH' in col_list:
        df['DAYS_BIRTH'] = -np.round(df['DAYS_BIRTH']//182.5)
    
    if 'CODE_GENDER' in col_list:
        df['CODE_GENDER'] = df['CODE_GENDER'].replace({'XNA':np.NaN})

    if 'NAME_EDUCATION_TYPE' in col_list:
        df['NAME_EDUCATION_TYPE'] = df['NAME_EDUCATION_TYPE'].replace({'Academic degree':'Higher education'})

    if 'DAYS_EMPLOYED' in col_list:
        df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace({365243:np.NaN})

    if 'DAYS_EMPLOYED' in col_list:
        df['DAYS_EMPLOYED'] = -np.round(df['DAYS_EMPLOYED']/182.5)   

    if 'DAYS_ID_PUBLISH' in col_list:
        df['DAYS_ID_PUBLISH'] = -np.round(df['DAYS_ID_PUBLISH']/182.5)   
    
    if 'DAYS_LAST_PHONE_CHANGE' in col_list:
        df['DAYS_LAST_PHONE_CHANGE'] = -np.round(df['DAYS_LAST_PHONE_CHANGE']/182.5)      

    if 'DAYS_REGISTRATION' in col_list:
        df['DAYS_REGISTRATION'] = -np.round(df['DAYS_REGISTRATION']/182.5)    

    if 'AMT_ANNUITY' in col_list and 'AMT_CREDIT' in col_list:
        df['AMT_ANN_CR_RATIO'] = df['AMT_ANNUITY'] / df['AMT_CREDIT'] * 100

    if 'AMT_CREDIT' in col_list and 'AMT_INCOME_TOTAL' in col_list:
        df['AMT_CR_INC_RATIO'] = df['AMT_CREDIT'] / df['AMT_INCOME_TOTAL'] * 100

    if 'AMT_ANNUITY' in col_list and 'PA_ACT_LOANS_ANN_SUM' in col_list and 'AMT_INCOME_TOTAL' in col_list:
        df['AMT_ANN_INC_RATIO'] = (df['AMT_ANNUITY'] + df['PA_ACT_LOANS_ANN_SUM']) / df['AMT_INCOME_TOTAL'] * 100  

    if 'OCCUPATION_TYPE' in col_list:
        def low_skill_personnel(row):
            if row['OCCUPATION_TYPE'] in ['Low-skill Laborers', 'Waiters/barmen staff']:
                return 1
            else:
                return 0
        df['OCCUPATION_LOW_SKILL'] = df.apply(low_skill_personnel, axis='columns')
        
    return df


import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
        
import os
for dirname, _, filenames in os.walk(os.getcwd()):
    for filename in filenames:
        print(os.path.join(dirname, filename))


DIR_NAME = '/kaggle/input/home-credit-default-risk/'
df_names = [fn[0:-4].lower() for fn in os.listdir(DIR_NAME) if fn.endswith('csv') and not fn.startswith('HomeCredit_')]
file_names = [os.path.join(DIR_NAME, fn) for fn in os.listdir(DIR_NAME) if fn.endswith('csv') and not fn.startswith('HomeCredit_')]

conx = duckdb.connect(database='home_credit.duckdb')

for i, fn in enumerate(file_names):
    conx.execute(f"CREATE TABLE {df_names[i]} AS SELECT * FROM read_csv_auto('{fn}', header=true)")


with open('/kaggle/input/home-credit-support-files/app_vars.json', 'r') as f:
    app_vars = json.load(f)

for k, v in app_vars.items():
    globals()[k] = v
    print(f'{k:<15}: {v[0:5]}')


feat_docs_new = ['FLAG_DOCUMENT_3', 'FLAG_DOCUMENT_6', 'FLAG_DOCUMENT_8']
feat_housing_new = ['FLOORSMIN_AVG', 'TOTALAREA_MODE', 'YEARS_BEGINEXPLUATATION_AVG', 'YEARS_BUILD_AVG', 
                    'EMERGENCYSTATE_MODE', 'FONDKAPREMONT_MODE', 'HOUSETYPE_MODE', 'WALLSMATERIAL_MODE'
                ]


pipelist_feat_loan = [
    ('impute_annuity', MeanMedianImputer(
        variables=['AMT_ANNUITY'], imputation_method='median')),

    ('drop_goods_price', DropFeatures(
        features_to_drop=['AMT_GOODS_PRICE'])),

    ('rare_hours', RareLabelEncoder(
        variables=['HOUR_APPR_PROCESS_START'], 
        tol=0.025, n_categories=10, replace_with='Rare', missing_values='ignore', ignore_format=True)),

    ('encode_dt_attrs', MeanEncoder(
        variables=['HOUR_APPR_PROCESS_START', 'WEEKDAY_APPR_PROCESS_START'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25)),

    ('encode_cr_type', OrdinalEncoder(
        variables=['NAME_CONTRACT_TYPE'], 
        encoding_method='arbitrary', missing_values='ignore', ignore_format=True, unseen='encode'))
]

pipelist_feat_income = [
    ('cap_income', ArbitraryOutlierCapper(
        max_capping_dict={'AMT_INCOME_TOTAL': 4e6}, missing_values='ignore')),

    ('rare_job_1', RareLabelEncoder(
        variables=['NAME_INCOME_TYPE'], 
        tol=0.025, n_categories=4, replace_with='Rare', missing_values='ignore', ignore_format=True)),

    ('rare_job_2', RareLabelEncoder(
        variables=['OCCUPATION_TYPE', 'ORGANIZATION_TYPE'], 
        tol=0.025, n_categories=8, replace_with='Rare', missing_values='ignore', ignore_format=True)),

    ('impute_job', CategoricalImputer(
        variables=['OCCUPATION_TYPE'], 
        imputation_method='missing', fill_value='Missing', return_object=True, ignore_format=True)),

    ('encode_work', MeanEncoder(
        variables=['NAME_INCOME_TYPE', 'OCCUPATION_TYPE', 'ORGANIZATION_TYPE'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25))
]

pipelist_feat_solvency = [
    ('bool_scores', AddMissingIndicator(
        variables=['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'], missing_only=False)),

    ('impute_scores', MeanMedianImputer(
        variables=['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'], imputation_method='median')),

    ('drop_dpd_obs', DropFeatures(
        features_to_drop=['DEF_60_CNT_SOCIAL_CIRCLE', 'OBS_30_CNT_SOCIAL_CIRCLE', 'OBS_60_CNT_SOCIAL_CIRCLE'])),

    ('bool_dpd_obs', AddMissingIndicator(
        variables=['DEF_30_CNT_SOCIAL_CIRCLE'], missing_only=False)),

    ('impute_dpd_obs', ArbitraryNumberImputer(variables=['DEF_30_CNT_SOCIAL_CIRCLE'], arbitrary_number=-1)),

    ('cap_dpd_obs', ArbitraryOutlierCapper(
        max_capping_dict={'DEF_30_CNT_SOCIAL_CIRCLE': 4}, missing_values='ignore'))
]

pipelist_feat_enquiries = [
    ('drop_enq', DropFeatures(
        features_to_drop=['AMT_REQ_CREDIT_BUREAU_WEEK', 'AMT_REQ_CREDIT_BUREAU_MON', 
                          'AMT_REQ_CREDIT_BUREAU_QRT', 'AMT_REQ_CREDIT_BUREAU_YEAR'])),

    ('enq_bool', AddMissingIndicator(
        variables=['AMT_REQ_CREDIT_BUREAU_HOUR', 'AMT_REQ_CREDIT_BUREAU_DAY'], missing_only=False)),

    ('impute_enq', ArbitraryNumberImputer(
        variables=['AMT_REQ_CREDIT_BUREAU_HOUR', 'AMT_REQ_CREDIT_BUREAU_DAY'], arbitrary_number=-1)),

    ('cap_enq', ArbitraryOutlierCapper(
        max_capping_dict={'AMT_REQ_CREDIT_BUREAU_HOUR': 1, 'AMT_REQ_CREDIT_BUREAU_DAY': 1}, missing_values='ignore'))
]

pipelist_feat_assets = [
    ('rare_housing', RareLabelEncoder(
        variables=['NAME_HOUSING_TYPE'], 
        tol=0.025, n_categories=3, replace_with='Rare', missing_values='ignore', ignore_format=True)),

    ('encode_housing_sit', MeanEncoder(
        variables=['NAME_HOUSING_TYPE'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25)),

    ('crop_car_age', ArbitraryOutlierCapper(
        max_capping_dict={'OWN_CAR_AGE': 3*12}, missing_values='ignore')),

    ('bool_car_age', AddMissingIndicator(
        variables=['OWN_CAR_AGE'], missing_only=False)),

    ('impute_car_age', ArbitraryNumberImputer(variables=['OWN_CAR_AGE'], arbitrary_number=-1))
]

pipelist_feat_geosocial = [
    ('drop_region_rating', DropFeatures(features_to_drop=['REGION_RATING_CLIENT']))
]

pipelist_feat_personal = [
    ('impute_gender', CategoricalImputer(
        variables=['CODE_GENDER'], imputation_method='frequent', return_object=True, ignore_format=True)),

    ('encode_gender', OrdinalEncoder(
        variables=['CODE_GENDER'], 
        encoding_method='arbitrary', missing_values='ignore', ignore_format=True, unseen='encode')),

    ('impute_fam_members', MeanMedianImputer(
        variables=['CNT_FAM_MEMBERS'], imputation_method='median')),

    ('cap_fam_members', ArbitraryOutlierCapper(
        max_capping_dict={'CNT_CHILDREN':3, 'CNT_FAM_MEMBERS':5}, missing_values='ignore')),

    ('encode_edu', MeanEncoder(
        variables=['NAME_EDUCATION_TYPE'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25)),

    ('encode_family_status', MeanEncoder(
        variables=['NAME_FAMILY_STATUS'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25)),

    ('impute_attend', CategoricalImputer(
        variables=['NAME_TYPE_SUITE'], 
        imputation_method='frequent', return_object=True, ignore_format=True)),

    ('rare_attend', RareLabelEncoder(
        variables=['NAME_TYPE_SUITE'], 
        tol=0.025, n_categories=3, replace_with='Rare', missing_values='ignore', ignore_format=True)),

    ('encode_attend', MeanEncoder(
        variables=['NAME_TYPE_SUITE'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25))
]

pipelist_feat_events = [
    ('bool_events', AddMissingIndicator(
        variables=['DAYS_EMPLOYED', 'DAYS_ID_PUBLISH', 'DAYS_LAST_PHONE_CHANGE', 'DAYS_REGISTRATION'], 
        missing_only=True)),
    ('impute_events', MeanMedianImputer(
        variables=['DAYS_EMPLOYED', 'DAYS_ID_PUBLISH', 'DAYS_LAST_PHONE_CHANGE', 'DAYS_REGISTRATION'], 
        imputation_method='mean'))
]

pipelist_feat_relocation = [
    ('drop_reloc', DropFeatures(
        features_to_drop=['LIVE_REGION_NOT_WORK_REGION', 'REG_REGION_NOT_LIVE_REGION', 'REG_REGION_NOT_WORK_REGION']))
]

pipelist_feat_docs = [
    ('drop_docs', DropFeatures(
        features_to_drop=list(set(feat_docs).difference(feat_docs_new))))
]

pipelist_feat_housing = [
    ('drop_housing', DropFeatures(
        features_to_drop=list(set(feat_housing).difference(feat_housing_new)))),

    ('bool_housing', AddMissingIndicator(
        variables=feat_housing_new, missing_only=True)),

    ('impute_housing_cat', CategoricalImputer(
        variables=['EMERGENCYSTATE_MODE', 'FONDKAPREMONT_MODE', 'HOUSETYPE_MODE', 'WALLSMATERIAL_MODE'],
        imputation_method='missing', fill_value='Missing', return_object=True, ignore_format=True)),
    
    ('impute_housing_num', MeanMedianImputer(
        variables=['FLOORSMIN_AVG', 'TOTALAREA_MODE', 'YEARS_BEGINEXPLUATATION_AVG', 'YEARS_BUILD_AVG'], 
        imputation_method='mean')),

    ('encode_housing', MeanEncoder(
        variables=['EMERGENCYSTATE_MODE', 'FONDKAPREMONT_MODE', 'HOUSETYPE_MODE', 'WALLSMATERIAL_MODE'], 
        missing_values='ignore', ignore_format=True, unseen='encode', smoothing=0.25))
]

pipelist_feat_contacts = [
    ('drop_contacts', DropFeatures(
        features_to_drop=['FLAG_MOBIL']))
]


pipelist_feat_preproc = (pipelist_feat_loan 
                         + pipelist_feat_income 
                         + pipelist_feat_solvency 
                         + pipelist_feat_enquiries
                         + pipelist_feat_assets
                         + pipelist_feat_geosocial
                         + pipelist_feat_personal
                         + pipelist_feat_events
                         + pipelist_feat_relocation
                         + pipelist_feat_docs
                         + pipelist_feat_housing
                         + pipelist_feat_contacts
)
col_list = (feat_loan 
            + feat_income 
            + feat_solvency 
            + feat_enquiries
            + feat_assets
            + feat_geosocial
            + feat_personal
            + feat_events
            + feat_relocation
            + feat_docs
            + feat_housing
            + feat_contacts
)


with open('/kaggle/input/home-credit-support-files/queries_train.sql', 'r') as f:
    query_train = f.read()

with open('/kaggle/input/home-credit-support-files/queries_test.sql', 'r') as f:
    query_test = f.read()

X_train = conx.execute(query_train).fetch_df()
X_test = conx.execute(query_test).fetch_df()

X_train = post_query_process(X_train)
X_test = post_query_process(X_test)

y_train = X_train['TARGET']
y_test = pd.concat([X_test['SK_ID_CURR'], pd.Series(np.empty(X_test.shape[0]), name='TARGET')], axis=1)

X_train = X_train.drop(columns='TARGET')

conx.close()


print(f'X_train: {X_train.shape}; X_test: {X_test.shape}')
print(f'y_train: {y_train.shape}; y_test: {y_test.shape}')


pd.concat([X_train.head(3), X_train.tail(3)])

pd.concat([X_test.head(3), X_test.tail(3)])

utils.info_ext(X_train, X_train.columns).loc['CB_HAS_MORTAGE':]

pipelist_feat_new = [
    ('impute_new_ratios', MeanMedianImputer(
        variables=['AMT_ANN_CR_RATIO', 'AMT_ANN_INC_RATIO'], imputation_method='median')),

    ('bool_new_feat', AddMissingIndicator(
        variables=['CB_DPD_FIRST_CNT', 'CB_DPD_FIRST_SUM', 'CB_DPD_LAST_CNT', 'CB_DPD_LAST_SUM',
        'PA_LOANS_APP_PCT', 'PA_LOANS_REF_PCT', 'PA_LOANS_UNU_PCT', 
        'PA_LOANS_APP_AVG', 'PA_LOANS_REF_AVG', 'PA_LOANS_UNU_AVG',
        'PA_LOANS_APP_SUM', 'PA_LOANS_REF_SUM', 'PA_LOANS_UNU_SUM',
        'PA_DAYS_DECISION_MAX', 'PA_INSURED_AVG', 'PA_LOANS_TERM_AVG', 'PA_LOANS_TERM_MAX', 'PA_PCT_RISK_AVG',
        'IP_LOANS_DAYS_LATE_AVG', 'IP_CC_DAYS_LATE_AVG', 'IP_LOANS_DPD', 'IP_CC_DPD',
        'CC_LOADING_AVG'], missing_only=False)),

    ('impute_new_feat', ArbitraryNumberImputer(
        variables=['CB_DPD_FIRST_CNT', 'CB_DPD_FIRST_SUM', 'CB_DPD_LAST_CNT', 'CB_DPD_LAST_SUM',
        'PA_LOANS_APP_PCT', 'PA_LOANS_REF_PCT', 'PA_LOANS_UNU_PCT', 
        'PA_LOANS_APP_AVG', 'PA_LOANS_REF_AVG', 'PA_LOANS_UNU_AVG',
        'PA_LOANS_APP_SUM', 'PA_LOANS_REF_SUM', 'PA_LOANS_UNU_SUM',
        'PA_DAYS_DECISION_MAX', 'PA_INSURED_AVG', 'PA_LOANS_TERM_AVG', 'PA_LOANS_TERM_MAX', 'PA_PCT_RISK_AVG',
        'IP_LOANS_DAYS_LATE_AVG', 'IP_CC_DAYS_LATE_AVG', 'IP_LOANS_DPD', 'IP_CC_DPD',
        'CC_LOADING_AVG'], arbitrary_number=0)),

    ('drop_ids', DropFeatures(
        features_to_drop=['SK_ID_CURR']))
]


pipelist_feat_preproc += pipelist_feat_new

pipe_feat_preproc = Pipeline(pipelist_feat_preproc)
pipe_feat_preproc.fit(X_train, y_train)

X_train_cln = pipe_feat_preproc.transform(X_train)
X_test_cln = pipe_feat_preproc.transform(X_test)

print(f'X_train: {X_train_cln.shape}; X_test: {X_test_cln.shape}')


xgb_mdl = XGBClassifier(
                booster='gbtree',
                tree_method='hist',
                verbosity=1,
                objective='binary:logistic',
                n_estimators=300,
                max_depth=6,
                learning_rate=0.15,
                min_child_weight=88.0,
                subsample=0.95,
                colsample_bytree=0.65,
                scale_pos_weight=1,
                reg_alpha=9.20,
                reg_lambda=1.5,
                gamma=0.65,
                importance_type='gain',
                n_jobs=None,
                seed=4567
)

pipelist_mdl = [('xgb_mdl', xgb_mdl)]
pipe_mdl = Pipeline(pipelist_feat_preproc + pipelist_mdl)
pipe_mdl.fit(X=X_train, y=y_train)


y_test['TARGET'] = pipe_mdl.predict_proba(X_test)[:, 1]
y_test.round(6).to_csv('submission.csv', index=False)

pd.concat([
    y_test['TARGET'].round(1).value_counts(),
    y_test['TARGET'].round(1).value_counts(normalize=True)*100], 
    axis=1
)