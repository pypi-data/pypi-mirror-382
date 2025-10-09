# -*- coding: utf-8 -*-
"""
Plotters Functions Module
Comprehensive collection of plotting and visualization utilities for data exploration and presentation
"""

# third-party data science imports
import pandas as pd
import numpy as np

# visualization imports
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# other plotters
from statsmodels.nonparametric.smoothers_lowess import lowess

def df_boxplotter(df_name, col_xplot, col_yplot, type_plot: int, *args):
    """create box plot to visualize outliers. type_plot: 0 for dist, 1 for money, 2 for general"""
    # usage: df_boxplotter(df, 'col_x', 'col_y', type_plot=0, 'horizontalalignment')
    # input: df_name - pandas DataFrame, col_xplot - column name for x-axis, col_yplot - column name for y-axis, type_plot - type of plot (0 for dist, 1 for money, 2 for general), args - optional arguments for plot customization
    # output: box plot figure
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    sns.boxplot(x=df_name[col_xplot], y=df_name[col_yplot], ax=ax)
    plt.title('{} box plot to visualise outliers'.format(col_yplot))
    
    if type_plot == 0:
        plt.ylabel('{} in miles'.format(col_yplot))
    elif type_plot == 1:
        plt.ylabel('{} in $'.format(col_yplot))
    else:
        plt.ylabel('{}'.format(col_yplot))
    
    if args:
        plt.xticks(rotation=0, horizontalalignment=args[0])
    
    ax.yaxis.grid(True)
    plt.savefig("Boxplot_x-{}_y-{}.png".format(col_xplot, col_yplot))
    plt.show()


def df_histplotter(df_name, col_plot, type_plot: int, bins=10, *args):
    """create histogram plot. type_plot: 0 for dist, 1 for money"""
    # usage: df_histplotter(df, 'col_name', type_plot=0, bins=20)
    # input: df_name - pandas DataFrame, col_plot - column name to plot, type_plot - type of plot (0 for dist, 1 for money), bins - number of bins
    # output: histogram figure
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    df_name[col_plot].hist(bins=bins, ax=ax)
    plt.title('{} histogram'.format(col_plot))
    
    if type_plot == 0:
        plt.xlabel('{} in miles'.format(col_plot))
    elif type_plot == 1:
        plt.xlabel('{} in $'.format(col_plot))
    else:
        plt.xlabel('{}'.format(col_plot))
    
    plt.ylabel('Frequency')
    ax.grid(True)
    plt.savefig("Histogram_{}.png".format(col_plot))
    plt.show()


def df_grouped_histplotter(df_name, col_groupby: str, col_plot: str, type_plot: int, bins=20):
    """create grouped histogram plots"""
    # usage: df_grouped_histplotter(df, 'col_groupby', 'col_plot', type_plot=0, bins=20)
    # input: df_name - pandas DataFrame, col_groupby - column name to group by, col_plot - column name to plot, type_plot - type of plot (0 for dist, 1 for money), bins - number of bins
    # output: grouped histogram figure
    groups = df_name.groupby(col_groupby)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    for name, group in groups:
        group[col_plot].hist(bins=bins, alpha=0.7, label=name, ax=ax)
    
    plt.title('{} histogram grouped by {}'.format(col_plot, col_groupby))
    plt.xlabel(col_plot)
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()


def df_grouped_barplotter(df_name, col_groupby: str, col_plot: str, type_plot: int):
    """create grouped bar plots"""
    # usage: df_grouped_barplotter(df, 'col_groupby', 'col_plot', type_plot=0)
    # input: df_name - pandas DataFrame, col_groupby - column name to group by, col_plot - column name to plot, type_plot - type of plot (0 for dist, 1 for money)
    # output: bar plot figure
    grouped_data = df_name.groupby(col_groupby)[col_plot].mean()
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    grouped_data.plot(kind='bar', ax=ax)
    plt.title('{} by {}'.format(col_plot, col_groupby))
    plt.xlabel(col_groupby)
    plt.ylabel(col_plot)
    plt.xticks(rotation=45)
    plt.show()


def df_scatterplotter(df_grouped, col_xplot, col_yplot):
    """create scatter plot between two variables"""
    # usage: df_scatterplotter(df, 'col_x', 'col_y')
    # input: df_grouped - pandas DataFrame with columns col_xplot and col_yplot
    # output: scatter plot figure
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    df_grouped.plot.scatter(x=col_xplot, y=col_yplot, ax=ax)
    plt.title('Scatter plot: {} vs {}'.format(col_xplot, col_yplot))
    plt.show()


def df_pairplot(df_name):
    """create pairplot for data exploration"""
    # usage: df_pairplot(df)
    # input: df - pandas DataFrame, with features to plot
    # output: pairplot figure
    sns.pairplot(df_name)
    plt.show()


def df_heatmap(df_name, col_list: list):
    """create heatmap for correlation matrix"""
    # usage: df_heatmap(df, ['col1', 'col2', 'col3'])
    # input: df - pandas DataFrame, col_list - list of column names to include in correlation
    # output: heatmap figure
    corr = df_name[col_list].corr()
    plt.figure(figsize=(10, 8), dpi=100)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title('Correlation Heatmap')
    plt.show()


def df_lowess_plotter(x, y, frac=0.1, title="LOWESS Smoothing"):
    """create LOWESS smoothed plot"""
    # usage: df_lowess_plotter(x, y, frac=0.1)
    # input: x - array-like, y - array-like, frac - smoothing parameter
    # output: LOWESS smoothed plot
    lowess_smoothed = lowess(y, x, frac=frac)
    smoothed_x = lowess_smoothed[:, 0]
    smoothed_y = lowess_smoothed[:, 1]   
    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(x, y, alpha=0.5, label='Data Points')
    plt.plot(smoothed_x, smoothed_y, color='red', label='LOWESS Smoothed', linewidth=2)
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid(True)
    plt.show()