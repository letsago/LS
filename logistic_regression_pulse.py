# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:09:52 2018

@author: 9yu6990
"""

import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt 
plt.rc("font", size=14)
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
import seaborn as sns
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)

data = pd.read_csv("LMB_pulse_forecast_data.csv") # change file name appropriately

data2 = data.drop(data.columns[[0, 1, 2, 3, 4, 5, 6, 7]], axis = 1, inplace = True)

data2 = pd.get_dummies(data, columns =['DO_OUTLIERS_EXIST', 'STD_DIFF_LEVEL', 'HISTORY_PRIOR_FIRST_OUTLIER', 'SIGNIFICANCE']) # read up on .get_dummies documentation if confused

# some cool visuals
sns.heatmap(data2.corr())
plt.show()

# split between feature inputs (X) and desired output (y)
X = data2.iloc[:,1:]
y = data2.iloc[:,0]

# split training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# denote classifier as Logistic regression
classifier = LogisticRegression(random_state=0)
classifier.fit(X_train, y_train)

# use classifier to predict outputs based on test set
y_pred = classifier.predict(X_test)

# output results of model prediction / read up on confusion_matrix documentation if confused
from sklearn.metrics import confusion_matrix
confusion_matrix = confusion_matrix(y_test, y_pred)
print(confusion_matrix)

print('Accuracy of logistic regression classifier on test set: '.format(classifier.score(X_test, y_test)))
