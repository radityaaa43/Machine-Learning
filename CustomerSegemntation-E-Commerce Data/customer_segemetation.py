# -*- coding: utf-8 -*-
"""Customer Segemetation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/180K5inau_AVlNsZ7lzx5aS-16EV_IjBs
"""

!pip install plotly==4.5.2

# Importation of useful libraries
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns

import random 
import datetime as dt
import re

from scipy.stats import chi2_contingency

from sklearn.preprocessing import LabelEncoder, MinMaxScaler, Normalizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score, accuracy_score, classification_report
from sklearn import preprocessing, model_selection, metrics, feature_selection
from sklearn.model_selection import GridSearchCV, learning_curve
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn import neighbors, linear_model, svm, tree, ensemble
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB


from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

import os

data = pd.read_csv('/content/data.csv', encoding="ISO-8859-1")
data.head()

data.info()

data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])

data.isna().sum()

data[data['CustomerID'].isna()].head()

data[data['Description'].isna()].head()

data[data['Description'].isna()].shape

"""In the Description column, if it has NaN value then give 0 value to UnitPrice"""

data[data['UnitPrice']==0]

"""And we see if description has NaN value it give 0 value for unit price."""

data[data['UnitPrice']==0]

data['UnitPrice'].describe()

"""In UnitPrice we have value < 0"""

data[data['UnitPrice']<0]

data = data[data['UnitPrice']>=0]
data = data[data['Quantity']>=0]

data.isnull().sum()

data[data['CustomerID'].isnull()]

data = data.dropna(subset={'CustomerID'})

data.isnull().sum()

"""Finishing for drop na.
Then, find duplicates value.
"""

print(f'Total duplicated entry: {data.duplicated().sum()}')

data = data[data.duplicated()==False]
print(f'Total duplicated entry after cleaning: {data.duplicated().sum()}')

data = data.astype({'CustomerID':str})

"""#Exploratory Analysis

Find the most selling
"""

data['Country'].unique()

"""#Find most customer country"""

customer_top10 = data.groupby('Country')['CustomerID'].count().sort_values(ascending=False).reset_index().head(10)
customer_top10

fig = px.bar(customer_top10, x=customer_top10['CustomerID'], y=customer_top10['Country'], orientation='h', color=customer_top10['Country'], title='Top 15 Customer')
fig.show()

fig = go.Figure()
fig.add_trace(go.Pie(labels=customer_top10['Country'], values=customer_top10['CustomerID']))
fig.show()

"""And we see 90.7% customers are from United Kingdom

#Find Most Selling Country
"""

country = data.groupby('Country')['Quantity'].sum().reset_index()
country = country.sort_values(['Quantity'], ascending=False).reset_index(drop=True)

top10_country = country[0:10]
top10_country

fig = px.bar(top10_country, y=top10_country['Country'], x=top10_country['Quantity'], color=top10_country['Country'], text='Quantity', orientation='h', title='Top 15 Selling')
fig.update(layout_coloraxis_showscale=False)
fig.show()

fig = go.Figure()
fig.add_trace(go.Pie(labels=top10_country['Country'], values=top10_country['Quantity']))
fig.show()

"""Here we see 84.6% items are selling to United Kingdom

#Find Most Selling Value Country
"""

data['TotalPrice'] = data['Quantity'] * data['UnitPrice']
data.head(15)

top_15 = data.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).reset_index().head(15)
top_15

fig = px.bar(top_15, x = top_15['TotalPrice'], y=top_15['Country'], text='TotalPrice', orientation='h', color=top_15['Country'], title='Top 15 Most Total Gross Amount Sales')
fig.show()

fig = go.Figure()
fig.add_trace(go.Pie(labels=top_15['Country'], values=top_15['TotalPrice']))
fig.show()

"""Here we see 83.2% total gross amount sales to United Kingdom

#RFM Analysis for Customer Segmentation

Recency
"""

data['Date'] = data['InvoiceDate'].apply(lambda x: x.date())
data.drop(columns='InvoiceDate', inplace=True)
data.head()

recency = data.groupby('CustomerID')['Date'].max().reset_index()
recency.columns = ['CustomerID', 'LastPurcashed']
recency.head()

now = dt.date(2021,8,13)
print(now)

recency['Recency'] = recency['LastPurcashed'].apply(lambda x : (now - x).days)
recency.drop(columns='LastPurcashed', inplace=True)

recency.head()

"""Frequency"""

frequency = data.drop_duplicates(['InvoiceNo', 'CustomerID'], keep='first')
frequency = frequency.groupby('CustomerID')['InvoiceNo'].count().reset_index()
frequency.columns = ['CustomerID', 'Frequency']
frequency.head()

"""Monetary"""

monetary = data.groupby('CustomerID')['TotalPrice'].sum().reset_index()
monetary.columns = ['CustomerID', 'Monetary']
monetary.head()

rfm = recency.merge(frequency, on='CustomerID')
rfm = rfm.merge(monetary, on='CustomerID')
rfm.head()

rfm.set_index('CustomerID', inplace=True)

rfm.info()

"""#Create RFM Tables"""

rfm_class = rfm
rfm_class['recency_score'] = pd.qcut(rfm_class['Recency'],5,labels=[5,4,3,2,1])
rfm_class['frequency_score'] = pd.qcut(rfm_class['Frequency'].rank(method="first"),5,labels=[1,2,3,4,5])
rfm_class['monetary_score'] = pd.qcut(rfm_class['Monetary'],5,labels=[1,2,3,4,5])
rfm_class['RFM_SCORE'] = (rfm_class['recency_score'].astype(str)+ rfm_class['frequency_score'].astype(str))

rfm_class.head()

"""Top Customer for Highest Monetary"""

sns.heatmap(rfm_class.corr(),cmap="YlGnBu",annot=True)

seg_map = {r'[1-2][1-2]': 'hibernating',
           r'[1-2][3-4]': 'at_Risk',
           r'[1-2]5': 'cant_loose',
           r'3[1-2]': 'about_to_sleep',
           r'33': 'need_attention',
           r'[3-4][4-5]': 'loyal_customers',
           r'41': 'promising',
           r'51': 'new_customers',
           r'[4-5][2-3]': 'potential_loyalists',
           r'5[4-5]': 'champions'}

rfm_class['segment'] = rfm_class['RFM_SCORE'].replace(seg_map, regex=True)
rfm_class.head()

customer_segment = pd.DataFrame(rfm_class['segment'].value_counts())
customer_segment = customer_segment.reset_index()
customer_segment.columns = ['segment','count']
customer_segment

#visualisasi
fig = px.treemap(customer_segment, path = ['segment'] , values='count') #membutuhkan update untuk treemap ke plotly 4.5.2
fig.data[0].textinfo = 'label+text+value'
fig.update_layout(title='Customer Segmentation')
fig.show()

"""#RFM Distribution"""

plt.figure(figsize=(12,10))
# Plot distribution of R
plt.subplot(3, 1, 1); sns.distplot(rfm_class['Recency'])
# Plot distribution of F
plt.subplot(3, 1, 2); sns.distplot(rfm_class['Frequency'])
# Plot distribution of M
plt.subplot(3, 1, 3); sns.distplot(rfm_class['Monetary'])
# Show the plot
plt.show()

fig = px.bar(customer_segment, x=customer_segment['count'].sort_values(ascending=False), 
              y='segment', orientation='h', color=customer_segment['segment'],
              text='count', title='Customer Segmentation')
 fig.update(layout_coloraxis_showscale=False)
 fig.show()

"""#K-Means Segmentation"""

k_clustering = rfm_class[['recency_score', 'frequency_score', 'monetary_score']].copy()
k_clustering

scaler = StandardScaler()
data_scaled = scaler.fit_transform(k_clustering)
data_scaled = pd.DataFrame(data_scaled)
data_scaled.head()

"""#Elbow to find n_clusters

"""

elbow = []
for i in range (1, 15):
  kmeans = KMeans(n_clusters=i, init="k-means++", random_state=0)
  kmeans.fit(data_scaled)
  labels = kmeans.labels_ 
  elbow.append(kmeans.inertia_)

plt.plot(range(1,15), elbow, marker="*")
plt.xlabel('K')
plt.ylabel('K-Means Inertia')
plt.title('Elbow Method For Optimal k')
plt.show()

"""from this picture, we see n_cluster = 4"""

for num in range(2,16):
    clusters = KMeans(n_clusters=num,random_state=0)
    labels = clusters.fit_predict(data_scaled)
    
    sil_avg = silhouette_score(data_scaled, labels)
    print('For',num,'The Silhouette Score is =',sil_avg)

"""We observe from the elbow plot a sharp bend after the number of clusters increase by 2. Silhoutte Score is also the highest for 2 clusters.

But, there is also a significant reduce in cluster error as number of clusters increase from 2 to 6 and after 6, the reduction is not much.

So, we will choose n_clusters = 6 to properly segment our customers.

#K-Means with n_clusters = 6
"""

kmeans = KMeans(n_clusters=6)
kmeans.fit(data_scaled)
pred = kmeans.predict(data_scaled)

from sklearn.metrics import silhouette_score
score = silhouette_score (data_scaled, kmeans.labels_)
print("Score = ", score)

k_clustering['Cluster'] = pred
temp = k_clustering['Cluster']
rfm_class = rfm_class.join(temp)
rfm_class

rfm_class.groupby('Cluster').mean()

"""#**Decision Tree Classifier**"""

X = k_clustering.drop(columns='Cluster')
Y = k_clustering['Cluster']

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42, stratify=Y)

# instantiate the model
dc=DecisionTreeClassifier()
knn=KNeighborsClassifier(1)
# train a Gaussian Naive Bayes classifier on the training set
from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB()


m6 = 'DecisionTreeClassifier'
dt = DecisionTreeClassifier(criterion = 'entropy',random_state=0,max_depth = 6)
dt.fit(X_train, y_train)
dt_predicted = dt.predict(X_test)
dt_conf_matrix = confusion_matrix(y_test, dt_predicted)
dt_acc_score = accuracy_score(y_test, dt_predicted)
print("confussion matrix")
print(dt_conf_matrix)
print("\n")
print("Accuracy of DecisionTreeClassifier:",dt_acc_score*100,'\n')
print(classification_report(y_test,dt_predicted))

from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, dt_predicted)

print('Confusion matrix\n\n', cm)

print('\nTrue Positives(TP) = ', cm[0,0])

print('\nTrue Negatives(TN) = ', cm[1,1])

print('\nFalse Positives(FP) = ', cm[0,1])

print('\nFalse Negatives(FN) = ', cm[1,0])

"""#**KNN**"""

m5 = 'K-NeighborsClassifier'
knn = KNeighborsClassifier(n_neighbors=10)
knn.fit(X_train, y_train)
knn_predicted = knn.predict(X_test)
knn_conf_matrix = confusion_matrix(y_test, knn_predicted)
knn_acc_score = accuracy_score(y_test, knn_predicted)
print("confussion matrix")
print(knn_conf_matrix)
print("\n")
print("Accuracy of K-NeighborsClassifier:",knn_acc_score*100,'\n')
print(classification_report(y_test,knn_predicted))

# Print the Confusion Matrix and slice it into four pieces

from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, knn_predicted)

print('Confusion matrix\n\n', cm)

print('\nTrue Positives(TP) = ', cm[0,0])

print('\nTrue Negatives(TN) = ', cm[1,1])

print('\nFalse Positives(FP) = ', cm[0,1])

print('\nFalse Negatives(FN) = ', cm[1,0])

"""#**Gaussian Naive Bayes Classifier**"""

m2 = 'Naive Bayes'
gnb.fit(X_train,y_train)
nbpred = gnb.predict(X_test)
nb_conf_matrix = confusion_matrix(y_test, nbpred)
nb_acc_score = accuracy_score(y_test, nbpred)
print("confussion matrix")
print(nb_conf_matrix)
print("\n")
print("Accuracy of Naive Bayes model:",nb_acc_score*100,'\n')
print(classification_report(y_test,nbpred))

# Print the Confusion Matrix and slice it into four pieces

from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test,nbpred)

print('Confusion matrix\n\n', cm)

print('\nTrue Positives(TP) = ', cm[0,0])

print('\nTrue Negatives(TN) = ', cm[1,1])

print('\nFalse Positives(FP) = ', cm[0,1])

print('\nFalse Negatives(FN) = ', cm[1,0])

"""**Conclusion:**

We saw that using classification models like Logisitc Regression, KNeighborsClassifier, DecisionTree, we predicted the clusters for customers using the RFM dataset as the independent variable and cluster as the target variable. The clusters predicted by the classification models match perfectly with KMeans clustering. that our groups are right.
"""