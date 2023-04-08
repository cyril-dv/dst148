# Headhunter vacancies database analysis


## Project description
The project involves writing a number of SQL queries against a PostgresSQL database that contains data about IT vacancies published on HeadHunter recruitment website. The results of SQL queries are used to answer multiple-choice questions for a project and prepare the analysis of vacancies contained in the database (salary ranges, industries and key skills).

## Database schema
The schema contains five tables named vacancies, areas, employers, industries and employers_industries. The latter acting as a bridge table between employers and industries in a one-to-many relationship.

| Table | Description | Rows
| --- | --- | --- |
|vacancies|ID and name of a vacancies, list of key skills, salary range and employment type; area and employer foreign keys|49 197
|areas|ID and name of an area (city, region, country)|1 362
|employers|ID, name and location of an employer|23 501
|industries|ID and name of an industry|294
|employers_industries|IDs of employers and industries|32 333

Each attributes' data types are provided in ER diagram in the project's notebook.

## Data summary
The vacancies table contains about 50 thousand vacancies that are either directly (software development and engineering) or indirectly (data and boniness analytics, customer support) related to IT. The vast majority of job vacancies are in large cities where most employers headquarters are located. Most employers (72%) are offering full-time onsite position and looking for a candidate with up to three years of work experience. Excluding top 10 large national companies, each employer has posted three vacancies. Across all vacancies average salary offering ranged from 71 065 to 110537 rub. per month.