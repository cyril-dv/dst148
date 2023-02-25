# Headhunter resume database analysis

## Project description
The project involves analysis of a sample resume database provided by Headhunter job search and recruitment services website. The required steps in the analysis included data cleaning and manipulation to extract useful features from raw data, explanatory analysis of variables and their visualization using Seaborn, and detection of duplicates and outliers in data. The scope of performed tasks is considered to be a first stage in a process of creating a recommendation system that will match applicants and available vacancies.

## Data set
The initial dataset includes 12 variables and 44 744 records. The brief description of variables is presented below.

| Variable | Description |
| --- | --- |
|Пол, возраст|Raw string with age, sex and DoB|
|ЗП|Expected remuneration and currency
|Ищет работу на должность|Wanted job position
|Город, переезд, командировки|City, willingness to relocate/work travel
|Занятость|Type of employment
|График|Preffered work schedule
|Опыт работы|Work experience
|Последнее/нынешнее место работы|Current/last place of employment
|Последняя/нынешняя должность|Current/last job position
|Образование и ВУЗ|Education details
|Обновление резюме|Last updated date
|Авто|Car ownership information

The copy of the dataset is available for download from [Google Drive](https://drive.google.com/file/d/1zwCywLyHqQSk4ldrFeptVtQoeUFthFEy/view?usp=share_link).

## Data manipulation
The data is loaded in Pandas dataframe, variable are examined and raw strings are separated into separate variables, including dummy variables. The expected remuneration is transformed into local currency using prevailing market exchange rates contained in a separate dataframe.

## EDA and data visualization
For most prominent continuous variables -- age, work experience and expected remuneration -- data distribution is examined using histograms and potential outlier values are identified. Different levels of expected remuneration are studied based on values of numerous categorical variables extracted from a previous step.

## Outlier detection
Based on previously identified information the dataset is cleaned from duplicated rows; outliers and values that don't make practical sense are removed and null values are filled with appropriate substitutions.

## Results
The initial dataset that contained many raw strings and combined fields has been prepared for further analysis and developing a machine learning algorithm for recommendations. During the work on dataset the data for most important variables has been visualized and outlier values were uncovered. Most of data manipulation was performed using UDFs and DataFrame's apply() method and the graphs were prepared using Seaborn library with minor custom adjustments using Matplotlib's axes objects.