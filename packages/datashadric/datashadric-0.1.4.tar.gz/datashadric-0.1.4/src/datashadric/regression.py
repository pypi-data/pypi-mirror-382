# -*- coding: utf-8 -*-
"""
Regression Analysis Functions Module
Comprehensive collection of regression analysis utilities for model building, validation, and diagnostics
"""

# statistical analysis imports
import statsmodels.formula.api as smfapi
import statsmodels.api as smapi
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# third-party data science imports
import pandas as pd
import numpy as np
from scipy import stats

# visualization imports
import matplotlib.pyplot as plt


def lr_check_homoscedasticity(fitted, resid, *args):
    """check homoscedasticity assumption in linear regression"""
    # usage: lr_check_homoscedasticity(fitted, resid)
    # input: fitted - fitted values from regression model, resid - residuals from regression model, args - optional arguments for plot customization
    # output: residuals vs fitted values plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(fitted, resid)
    ax.axhline(y=0, color='red', linestyle='--')
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    ax.set_title('Residuals vs Fitted Values')
    plt.show()


def lr_check_normality(resid):
    """check normality of residuals"""
    # usage: lr_check_normality(resid)
    # input: resid - residuals from regression model
    # output: Shapiro-Wilk test statistic and p-value
    from scipy import stats
    stat, p_value = stats.shapiro(resid)
    print(f"Shapiro-Wilk test for residuals:")
    print(f"Statistic: {stat:.4f}, p-value: {p_value:.4f}")
    
    return stat, p_value


def lr_qqplots_normality(resid):
    """create q-q plots to check normality of residuals"""
    # usage: lr_qqplots_normality(resid)
    # input: resid - residuals from regression model
    # output: q-q plot figure
    fig, ax = plt.subplots(figsize=(8, 6))
    stats.probplot(resid, dist="norm", plot=ax)
    plt.title('Q-Q Plot of Residuals')
    plt.show()


def lr_post_hoc_test(df_name, col_response, col_predictor, alpha: float):
    """perform post-hoc test for anova"""
    # usage: lr_post_hoc_test(df, 'response_col', 'predictor_col', alpha=0.05)
    # input: df_name - pandas DataFrame, col_response - response variable column name, col_predictor - categorical predictor column name, alpha - significance level
    # output: Tukey HSD test results
    tukey_results = pairwise_tukeyhsd(
        endog=df_name[col_response],
        groups=df_name[col_predictor],
        alpha=alpha
    )
    print(tukey_results)

    return tukey_results


def lr_ols_model(df_name, col_response: str, col_cont_predictors: list, col_cat_predictors: list):
    """build ols regression model"""
    # usage: lr_ols_model(df, 'response_col', ['cont1', 'cont2'], ['cat1', 'cat2'])
    # input: df_name - pandas DataFrame, col_response - response variable column name, col_cont_predictors - list of continuous predictor column names, col_cat_predictors - list of categorical predictor column names
    # output: dictionary with model summary, fitted values, residuals, r-squared, adjusted r-squared
    # add constant to categorical predictors
    
    # prepare formula
    predictors = col_cont_predictors + col_cat_predictors
    formula = f"{col_response} ~ {' + '.join(predictors)}"
    
    # fit model
    model = smfapi.ols(formula, data=df_name).fit()
    print(model.summary())
    
    return {
        'model': model,
        'formula': formula,
        'fitted_values': model.fittedvalues,
        'residuals': model.resid,
        'r_squared': model.rsquared,
        'adj_r_squared': model.rsquared_adj
    }


def lr_glm_model(df_name, col_response: str, col_cont_predictors: list, col_cat_predictors: list, family):
    """build glm regression model"""
    # usage: lr_glm_model(df, 'response_col', ['cont1', 'cont2'], ['cat1', 'cat2'], smapi.families.Binomial())
    # input: df_name - pandas DataFrame, col_response - response variable column name, col_cont_predictors - list of continuous predictor column names, col_cat_predictors - list of categorical predictor column names, family - statsmodels family object (e.g., smapi.families.Binomial())
    # output: dictionary with model details
    # add constant to categorical predictors
    
    # prepare formula
    predictors = col_cont_predictors + col_cat_predictors
    formula = f"{col_response} ~ {' + '.join(predictors)}"
    
    # fit model
    model = smfapi.glm(formula, data=df_name, family=family).fit()
    print(model.summary())
    
    return {
        'model': model,
        'formula': formula,
        'fitted_values': model.fittedvalues,
        'residuals': model.resid_response,
        'r_squared': model.rsquared,
        'adj_r_squared': model.rsquared_adj
    }