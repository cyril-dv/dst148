# Credit default prediction modelling


## Project description
The final project involves the development of credit default risk model for a retail bank using a publicly available data from [the Kaggle competition](https://www.kaggle.com/competitions/home-credit-default-risk). The source data set contains information about current and past loan applications in seven tables with over 200 variables describing applicant characteristics, credit history and behavior traits. The main table with current loan applications contains 122 variables that are divided into 12 groups for easier EDA and feature selection. 

Using gradient boosted decision trees the model is developed to predict the target variable that is described by data provider as an occurrence of a late payment of more than X days on at least one of the first Y installments of the loan in the sample. Prediction by the model, expressed as a probability of positive event, is evaluated using area under the ROC Curve metric.

The following tools were used for data preparation, feature selection and model selection:
* [Duckdb](https://duckdb.org/) &mdash; An in-process analytical database for feature creation;
* [Feature-engine](https://feature-engine.trainindata.com/) &mdash; An library with scikit-learn API for feature creation, transformation, and selection;
* [XGBoost](https://xgboost.readthedocs.io/) &mdash; A gradient boosting algorithm for linear models and decision trees;
* [Optuna](https://optuna.org/) &mdash; A framework for hyperparameter optimization;
* [Joblib](https://joblib.readthedocs.io/) &mdash; Serialization of a trained model's pipeline for future inference.


## Dataset
The table below provides an overview of the source data.

| Table | Variables | Rows | Description |
| --- | --- | --- | --- |
|application_train / application_test|122|307 511 / 48 744|Current loan application information, including loan characteristics; applicants income, housing and family details;|
|bureau|17|1 716 428|Client's current and past loans statistics from credit bureau|
|bureau_balance|3|27 299 925|Monthly status update on each of the loans in credit bureau history|
|credit_card_balance|23|3 840 312|Monthly credit card loans details, including spending habits|
|installments_payments|8|13 605 401|Payment history on current and previous loans|
|pos_cash_balance|8|10 001 358|Montly history on cash and POS loans|
|previous_application|37|1 670 214|Past loan applications - approved and unapproved - of current prospective clients|


## Project steps
The following steps were taken to create the final model: 
* Creation of a local database from separate comma-separated files;
* Explanatory data analysis of variables in the main table and preparation of feature engineering steps;
* Explanatory data analysis of variables in related tables and selection of potential new features;
* Preparation of a SQL query to load data along with new features;
* Feature selection using cross validation and AUC ROC metric;
* Search of best hyperparameterts;
* Model creation and its serizlization;
* Predicting target values for test data and submitting results to Kaggle.


## Results
The final model achieves the value of 0.78 AUC ROC during cross validation and the value of 0.7732 on test data.
