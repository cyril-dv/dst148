# Clusterization of online retailer customers


## Project description
Given the popular dataset of UK online retailer transactions ([E-Commerce Data](https://www.kaggle.com/datasets/carrie1/ecommerce-data)) the cluster analysis of customer characteristics is performed in order to automate the creation of RFM models of consumer behaviour.


## Dataset
The dataset contains 8 variables that describe a single transaction within an order.

| Variable | Description
| --- | --- |
|InvoiceNo|Invoice ID|
|StockCode|Product ID|
|Description|Product description|
|Quantity|Quantity ordered|
|InvoiceDate|Invoice date|
|UnitPrice|Product unit price|
|CustomerID|Customer ID|
|Country|Customers' location when placing an order|


## Project steps
In order to perform customer clusterization the following steps were carried out: 
* data clean-up (missing values, negative order quantity and amounts, special transactions);
* EDA (order characteristics, revenue by country, top products);
* calculation of RFM attributes;
* feature reduction using PCA and TSNE;
* customer clusterization using reduced sample space attributes using K-Means, Agglomerative clustering and DBSCAN;
* evaluation of clusterization results using Silhouette coefficient for various combinations of dimensionality reduction and clusterization methods;
* visualization and interpretation of the best resulting cluster.


## Results
Different dimensionality reduction techniques are tested and then used to perform cluster segmentation for RFM analysis. The results from three clusterization methods are evaluated using Silhouette score to choose the best clustering approach. Then, using the distribution of customers' RFM attributes within each cluster, the customer profile is described.