# New York City Taxi Trip Duration


## Project description 
The project involves predicting the duration of taxi rides using a copy of [New York City Taxi Trip Duration](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/overview) dataset and answering a predetermined list of step-by-step questions on learning management system. The models used in this project include: linear regression (with polynomial features and L2 regularization), decision trees, random forest and gradient boosted decision trees. The metric used to measure a model's performance, per Kaggle competition rules, is root mean squared log error (RMSLE).


## Dataset
The dataset contains 11 variables that identify a trip and specify pick-up and drop-off coordinates.

| Variable | Description
| --- | --- |
|id|A unique identifier for each trip|
|vendor_id|A code indicating the provider associated with the trip record|
|pickup_datetime|Date and time when the meter was engaged|
|dropoff_datetime|Date and time when the meter was disengaged|
|passenger_count|The number of passengers in the vehicle (driver entered value)|
|pickup_longitude|The longitude where the meter was engaged|
|pickup_latitude|The latitude where the meter was engaged|
|dropoff_longitude|The longitude where the meter was disengaged|
|dropoff_latitude|The latitude where the meter was disengaged|
|store_and_fwd_flag|This flag indicates whether the trip record was held in vehicle memory before sending to the vendor because the vehicle did not have a connection to the server (Y=store and forward; N=not a store and forward trip)|
|trip_duration|duration of the trip in seconds|


## Project steps
In order to answer project's questions the following steps were carried out: 
* EDA with matplotlib graphs;
* outlier detection;
* feature generation (date and time attributes, geocoding and clustering);
* feature selection (using sklearn's SelectKBest);
* hyperparameter search;
* model estimation (incl. the above mentioned models and XGBoost).


## Results
Through a series of prepared questions, the project showcases a typical DS workflow for regression-type models focusing on feature engineering using domain knowledge and best model selection.