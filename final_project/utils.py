import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

from xgboost import XGBClassifier

import warnings



def info_ext(df, columns):
    df_out = pd.DataFrame({
                'dtype': df[columns].dtypes, 
                'obs': df[columns].count(), 
                'nulls': df[columns].isna().sum(),
                'nulls_pct': (df[columns].isna().sum() / df[columns].shape[0]).round(4)
            })
    return df_out



def top_unique_values(df, topvals=5, dropna=True):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        max_width = pd.get_option('display.max_colwidth') - 10
        col_names = ['Unique values'] + ['Top ' + str(num) for num in range(1, topvals + 1)] + ['Other']
        df_out = pd.DataFrame(columns=col_names)
        cols = df.columns
        for col in cols:
            top_values = pd.DataFrame(df[col].value_counts(dropna=dropna, normalize=True)).iloc[0:topvals]
            lst = []
            lst.append(df[col].nunique(dropna=dropna))
            for r in top_values.itertuples():
                i = str(r[0])[0:max_width] + ' (' + str(f'{r[1]:.1%}') + ')'
                lst.append(i)
            while len(lst) <= topvals:
                lst.append('\u2013')
            remainder = 1 - top_values.sum().iloc[0]
            if remainder != 0:
                lst.append(str(f'{remainder:.1%}'))
            else:
                lst.append('\u2013')
            row = (col, lst)
            df_out = pd.concat(
                [df_out, pd.DataFrame.from_dict(dict([row]), orient='index', columns=col_names)], 
                axis=0
            )
    return df_out



def iqr_outliers(df):
    vars = df.select_dtypes(include=[np.number]).columns
    df_out = df[vars].agg(
                lambda x: [
                    np.min(x), 
                    np.nanpercentile(x, 25), 
                    np.nanmean(x), 
                    np.nanmedian(x),
                    np.nanpercentile(x, 75), 
                    np.max(x),
                    np.nanstd(x)
                ])
    df_out.index = ['min', 'Q1', 'mean', 'median', 'Q3', 'max', 'std']
    df_out = df_out.transpose()
    
    lst = []
    for idx in df_out.index:
        row = (np.sum(df[idx] < df_out.loc[idx, 'Q1'] 
                      - 1.5 * (df_out.loc[idx, 'Q3'] - df_out.loc[idx, 'Q1'])),
               np.sum(df[idx] > df_out.loc[idx, 'Q3'] 
                      + 1.5 * (df_out.loc[idx, 'Q3'] - df_out.loc[idx, 'Q1']))
            )
        lst.append(row)
    outliers = pd.DataFrame(
        lst, 
        columns=['Values < 1.5IQR', 'Values > 1.5IQR'], 
        index=vars
    )
    df_out = (pd.concat([df_out, outliers], axis=1))
    return df_out



def col_desc(df):
    if isinstance(df['Special'], float):
        return df['Description']
    else:
        return df['Description'] + ' ' + df['Special']



def corr_cols(df, columns, incl_target=True):
    if incl_target:
        cols = columns + ['TARGET']
    else:
        cols = columns
    
    cols_name = df[cols].select_dtypes(exclude=['object', 'string']).columns
    
    corr_matrix = np.tril(df[cols].corr(method='pearson', numeric_only=True))
    corr_matrix[corr_matrix == 0] = np.NaN
    np.fill_diagonal(corr_matrix, np.NaN)

    if corr_matrix.shape[0] > 24:
        fig_size = 16
    elif corr_matrix.shape[0] > 12:
        fig_size = 8
    else:
        fig_size = 4

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    sns.heatmap(
        data=corr_matrix, 
        vmin=-1, 
        vmax=1,
        fmt='.2f', 
        cbar=False,
        cmap='RdBu_r', 
        linewidths=0.5, 
        annot=True, 
        annot_kws={'fontsize':'x-small'},
        xticklabels=cols_name,
        yticklabels=cols_name,
        robust=True,
        ax=ax
    )
    
    ax.set_xticklabels(cols_name, fontsize='x-small')
    ax.set_yticklabels(cols_name, fontsize='x-small')
    ax.set_title('Correlation matrix', fontsize='medium', fontweight='bold');



def numvar_plot(df, column, log_scale=False):
    boxplot_dict = {
        'saturation': 0.1,
        'showmeans': True,
        'width': 0.5,
        'fliersize': 6,
        'boxprops': {'facecolor': 'C0', 'edgecolor': '#4C4D4E', 'linewidth': 1.5},
        'flierprops': {'marker': '.'},
        'meanprops': {'marker': '8', 'markerfacecolor': 'w', 'markeredgecolor': '#4C4D4E', 'markeredgewidth': 0.75}
    }
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    sns.boxplot(x=df[column], **boxplot_dict, log_scale=log_scale, ax=ax1)
    sns.kdeplot(x=df[column], hue=df['TARGET'], common_norm=False, bw_adjust=1.5, log_scale=log_scale, ax=ax2)
    
    fig.suptitle(f'Distribution of "{column}"', fontsize='medium', fontweight='bold');



def catvar_plot(df, column):
    if df[column].nunique() > 20:
        palette_name = 'viridis'
    else:
        palette_name = 'tab20'
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    sns.barplot(y=df['TARGET'], hue=df[column].fillna('NaN').astype('category'), errorbar=None, estimator='count', palette=palette_name, legend=False, ax=ax1)
    sns.barplot(y=df['TARGET'], hue=df[column].fillna('NaN').astype('category'), errorbar=None, estimator='mean', palette=palette_name, legend=True, ax=ax2)
    
    ax2.legend(bbox_to_anchor=(0.5, 0.07), loc='upper center', ncols=5, mode=None, fontsize='small', bbox_transform=fig.transFigure)
    ax1.set_ylabel('Count')
    ax2.set_ylabel('TARGET mean')
    fig.suptitle(f'Characteristics of "{column}"', fontsize='medium', fontweight='bold');



def select_vars(df, numeric=True, cat_lim=50, dropna=False):
    selected_vars = []
    for col in df.columns:
        if df[col].nunique(dropna=dropna) > cat_lim:
            selected_vars.append(col)
    if numeric:
        return df.loc[:, selected_vars]
    else:
        return df.loc[:, df.columns.difference(selected_vars)]



def default_model_cv(pipelist, X, y):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=4567)
    xgb_default = XGBClassifier(
                    learning_rate=0.2,
                    n_estimators=100,
                    max_depth=4,
                    min_child_weight=4,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    objective='binary:logistic',
                    scale_pos_weight=2,
                    importance_type='gain',
                    n_jobs=None,
                    seed=4567
                )

    pipelist_mdl = [('default_xgb', xgb_default)]
    pipe_cv = Pipeline(pipelist + pipelist_mdl)

    cv_res = cross_val_score(pipe_cv, X=X, y=y, scoring='roc_auc', cv=cv, n_jobs=1)

    print(f'Cross-validation mean AUC ROC: {np.mean(cv_res):.4f} ({np.min(cv_res):.4f}-{np.max(cv_res):.4f})')

    pipe_cv.fit(X=X, y=y);
    
    return pd.DataFrame({
            'features': pipe_cv._final_estimator.feature_names_in_,
            'importance': pipe_cv._final_estimator.feature_importances_*100
        }).sort_values(by='importance', ascending=False).reset_index(drop=True)