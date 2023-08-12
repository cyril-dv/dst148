# Classification of banking clients


## Project description
The project's goal involves performing binary classification problem for banking clients using a copy of [Bank marketing campaigns dataset](https://www.kaggle.com/datasets/volodymyrgavrysh/bank-marketing-campaigns-dataset) dataset. The target variable is whether or not a client opened up a deposit account with a bank during current marketing campaign. Some of the DS steps were not carried out in full while others were intentionally performed erroneously (e.g. fitting transformers on the test data) in order to answer a predetermined list of step-by-step questions.


## Dataset
The dataset contains 16 variables which describe client's characteristics and list results of the previous marketing campaign carried out by the bank.

| Variable | Description
| --- | --- |
|age|Client's age|
|job|Current occupation|
|marital|Marital status|
|education|Attained education level|
|default|Client defaulted on current loan|
|housing|Client has house loan|
|loan|Client has consumer loan|
|balance|Account balance|
|contact|How client was contacted during last campaign|
|month|Month when last contact was made|
|day_of_week|Day when last contact was made|
|duration|Duration of last contact in seconds|
|campaign|Number of contacts during last campaign|
|pdays|Number of days elapsed since last contact|
|previous|Total number of contacts made before this campaign|
|poutcome|Outcome of the previous marketing campaign|


## Project steps
In order to answer project's questions the following steps were carried out: exploratory data analysis, identification of missing values and outliers and feature transformation and selection. Using SelectKBest with ANOVA F-values top 15 features were selected and used in logistic regression, decision trees and random forest models. Model's default hyperparametrs were then optimized using grid search and Optuna.


## Results
The project showcases various techniques available for hyperparameter optimization (from basic grid search, gradient boosting to Optuna set-up) within sklearn's composite transformers and pipelines.