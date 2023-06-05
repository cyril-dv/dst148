# Prediction of reviewer scores on booking.com


## Project description
Project's aim is to build a student's first predictive model using a copy of [515K Hotel Reviews Data in Europe](https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe) dataset and use its results to make a submission to [Kaggle competition](https://www.kaggle.com/competitions/sf-booking/overview). The dependent variable &ndash; reviewer's score &ndash; is estimated with the suggested random forest algorithm after exploratory data analysis and feature engineering is performed. 


## Dataset
The dataset contains 17 variables describing the hotel and its characteristics, reviewers' information and calculated measures such as total number of reviews a hotel received. The review itself consists of textual description, chosen tags and a score.

| Variable | Description
| --- | --- |
|hotel_address|Address of hotel|
|review_date|Date when reviewer posted the corresponding review|
|average_score|Average score of the hotel, calculated based on the latest comment in the last year|
|hotel_name|Name of hotel|
|reviewer_nationality|Nationality of reviewer|
|negative_review|Negative review the reviewer gave to the hotel. If the reviewer does not give the negative review, then it should be: 'No Negative'|
|review_total_negative_word_counts|Total number of words in the negative review|
|positive_review|Positive Review the reviewer gave to the hotel. If the reviewer does not give the negative review, then it should be: 'No Positive'|
|review_total_positive_word_counts|Total number of words in the positive review|
|reviewer_score|Score the reviewer has given to the hotel, based on his/her experience|
|total_number_of_reviews_reviewer_has_given|Number of reviews the reviewers has given in the past|
|total_number_of_reviews|Total number of valid reviews the hotel has|
|tags|Tags reviewer gave the hotel|
|days_since_review|Duration between the review date and scrape date|
|additional_number_of_scoring|There are also some guests who just made a scoring on the service rather than a review. This number indicates how many valid scores without review in there|
|lat|Latitude of the hotel|
|lng|longtitude of the hotel|


## Project steps
In order to build the final model, the following steps were performed: exploratory data analysis (calculation of descriptive statistics, identification of duplicates and outliers), feature extraction from existing variables and creation of a new ones, feature selection and model specification and estimation. 


## Results
Using sklearn's random forest regressor with chosen dependent variables produced the model that has train and test MAPE of approximately 12.5.