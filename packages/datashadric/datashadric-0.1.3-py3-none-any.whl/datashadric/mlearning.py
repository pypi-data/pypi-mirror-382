# -*- coding: utf-8 -*-
"""
Machine Learning Functions Module
Comprehensive collection of machine learning utilities for model training, evaluation, and prediction
"""

# third-party machine learning imports
import sklearn.linear_model as skllinmod
import sklearn.naive_bayes as sklnvbys
import sklearn.metrics as sklmtrcs
import sklearn.model_selection as sklmodslct

# third-party data science imports
import pandas as pd
import numpy as np

# visualization imports
import matplotlib.pyplot as plt
import seaborn as sns

# regression and preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# clustering algorithms
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# outlier detection and neighbor analysis
from sklearn.neighbors import NearestNeighbors, LocalOutlierFactor
from sklearn.ensemble import IsolationForest


def logr_predictor(df_name, log_regression_model: dict):
    """make predictions using logistic regression model"""
    # usage: logr_predictor(df, log_regression_model)
    # input: df - pandas DataFrame, log_regression_model - output from logr_train_test_split and model fitting
    # output: dictionary with predictions and probabilities
    model = log_regression_model['model']
    X = log_regression_model['X_test']
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    return {
        'predictions': predictions,
        'probabilities': probabilities
    }


def logr_classifier(df_name, log_regression_model: dict):
    """classify using logistic regression model"""
    # usage: logr_classifier(df, log_regression_model)
    # input: df - pandas DataFrame, log_regression_model - output from logr_train_test_split and model fitting
    # output: dictionary with accuracy, precision, recall, f1_score
    predictions = logr_predictor(df_name, log_regression_model)
    y_true = log_regression_model['y_test']
    y_pred = predictions['predictions']
    
    accuracy = sklmtrcs.accuracy_score(y_true, y_pred)
    precision = sklmtrcs.precision_score(y_true, y_pred, average='weighted')
    recall = sklmtrcs.recall_score(y_true, y_pred, average='weighted')
    f1 = sklmtrcs.f1_score(y_true, y_pred, average='weighted')
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }


def logr_train_test_split(df_name, col_response, col_predictor, test_size: float):
    """split data for logistic regression training and testing"""
    # usage: logr_train_test_split(df, 'response_col', 'predictor_col', test_size=0.2)
    # input: df - pandas DataFrame, col_response - response column name, col_predictor - predictor column name, test_size - proportion of data to use for testing
    # output: dictionary with X_train, X_test, y_train, y_test
    X = df_name[col_predictor]
    y = df_name[col_response]
    
    X_train, X_test, y_train, y_test = sklmodslct.train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }


def ml_train_test_split(df_name, col_target, test_size: float):
    """generic train test split for machine learning"""
    # usage: ml_train_test_split(df, 'target_col', test_size=0.2)
    # input: df - pandas DataFrame, col_target - target column name, test_size - proportion of data to use for testing
    # output: dictionary with X_train, X_test, y_train, y_test
    feature_cols = [col for col in df_name.columns if col != col_target]
    X = df_name[feature_cols]
    y = df_name[col_target]
    
    X_train, X_test, y_train, y_test = sklmodslct.train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }


def ml_naive_bayes_model(train_test_split_nm):
    """build naive bayes model"""
    # usage: ml_naive_bayes_model(train_test_split_nm)
    # input: output from ml_train_test_split
    # output: dictionary with model, train_predictions, test_predictions
    model = sklnvbys.GaussianNB()
    model.fit(train_test_split_nm['X_train'], train_test_split_nm['y_train'])
    
    train_predictions = model.predict(train_test_split_nm['X_train'])
    test_predictions = model.predict(train_test_split_nm['X_test'])
    
    return {
        'model': model,
        'train_predictions': train_predictions,
        'test_predictions': test_predictions,
        'X_train': train_test_split_nm['X_train'],
        'X_test': train_test_split_nm['X_test'],
        'y_train': train_test_split_nm['y_train'],
        'y_test': train_test_split_nm['y_test']
    }


def ml_naive_bayes_metrics(naive_bayes_nm):
    """calculate metrics for naive bayes model"""
    # usage: ml_naive_bayes_metrics(naive_bayes_nm)
    # input: output from ml_naive_bayes_model
    # output: dictionary with accuracy, precision, recall, f1_score
    y_true = naive_bayes_nm['y_test']
    y_pred = naive_bayes_nm['test_predictions']
    
    accuracy = sklmtrcs.accuracy_score(y_true, y_pred)
    precision = sklmtrcs.precision_score(y_true, y_pred, average='weighted')
    recall = sklmtrcs.recall_score(y_true, y_pred, average='weighted')
    f1 = sklmtrcs.f1_score(y_true, y_pred, average='weighted')
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }


def ml_naive_bayes_confusion(naive_bayes_nm):
    """create confusion matrix for naive bayes model"""
    # usage: ml_naive_bayes_confusion(naive_bayes_nm)
    # input: output from ml_naive_bayes_model
    # output: confusion matrix plot
    y_true = naive_bayes_nm['y_test']
    y_pred = naive_bayes_nm['test_predictions']
    
    cm = sklmtrcs.confusion_matrix(y_true, y_pred)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()
    
    return cm

def ml_naive_bayes_roc(naive_bayes_nm):
    """plot ROC curve for naive bayes model"""
    # usage: ml_naive_bayes_roc(naive_bayes_nm)
    # input: output from ml_naive_bayes_model
    # output: ROC curve plot
    y_true = naive_bayes_nm['y_test']
    y_scores = naive_bayes_nm['model'].predict_proba(naive_bayes_nm['X_test'])[:, 1]
    
    fpr, tpr, thresholds = sklmtrcs.roc_curve(y_true, y_scores)
    roc_auc = sklmtrcs.auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='red', linestyle='--')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')
    plt.show()
    
    return {
        'fpr': fpr,
        'tpr': tpr,
        'thresholds': thresholds,
        'roc_auc': roc_auc
    }

def ml_iforest_outlier_detection(df_name, col_list: list, contamination=0.1):
    """detect outliers using Isolation Forest"""
    # usage: ml_iforest_outlier_detection(df, ['col1', 'col2'], contamination=0.1)
    # input: df - pandas DataFrame, col_list - list of column names to use for outlier detection, contamination - proportion of outliers in the data
    # output: DataFrame with outlier labels
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    df_features = df_name[col_list]
    df_name['outlier'] = iso_forest.fit_predict(df_features)
    df_name['outlier'] = df_name['outlier'].map({1: 'inlier', -1: 'outlier'})
    
    return df_name[['outlier'] + col_list]


def ml_lof_outlier_detection(df_name, col_list: list, n_neighbors=20, contamination=0.1):
    """detect outliers using Local Outlier Factor"""
    # usage: ml_lof_outlier_detection(df, ['col1', 'col2'], n_neighbors=20, contamination=0.1)
    # input: df - pandas DataFrame, col_list - list of column names to use for outlier detection, n_neighbors - number of neighbors to use, contamination - proportion of outliers in the data
    # output: DataFrame with outlier labels
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    df_features = df_name[col_list]
    df_name['outlier'] = lof.fit_predict(df_features)
    df_name['outlier'] = df_name['outlier'].map({1: 'inlier', -1: 'outlier'})
    
    return df_name[['outlier'] + col_list]


def ml_ks_score_evaluation(y_true, y_scores):
    """calculate K-S score for model evaluation"""
    # usage: ml_kscore_evaluation(y_true, y_scores)
    # input: y_true - true binary labels, y_scores - predicted scores or probabilities
    # output: K-S score value
    fpr, tpr, thresholds = sklmtrcs.roc_curve(y_true, y_scores)
    ks_score = max(tpr - fpr)
    print(f"K-S Score: {ks_score:.4f}")

    return ks_score

def ml_kmeans_clustering(df_name, col_list: list, n_clusters=3):
    """perform k-means clustering"""
    # usage: ml_kmeans_clustering(df, ['col1', 'col2'], n_clusters=3)
    # input: df - pandas DataFrame, col_list - list of column names to use for clustering, n_clusters - number of clusters
    # output: DataFrame with cluster labels
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df_features = df_name[col_list]
    df_name['cluster'] = kmeans.fit_predict(df_features)
    print(f"K-Means Clustering: {n_clusters} clusters found.")
    
    return df_name[['cluster'] + col_list]