# -*- coding: utf-8 -*-
"""
Stochastics Functions Module
Comprehensive collection of statistical analysis utilities for hypothesis testing, distributions, and statistical inference
"""

# standard library imports
import calendar as cal

# third-party data science imports
import datashadric
import pandas as pd
import numpy as np
from scipy import stats

# statistical analysis imports
from statsmodels.stats.outliers_influence import variance_inflation_factor as smvif
import statsmodels.tools.tools as smtools
import statsmodels.stats.multicomp as smmulti
from statsmodels.tools.tools import add_constant as smac

# visualization imports
import matplotlib.pyplot as plt


def df_gaussian_checks(df_name, col_name, *args):
    """check if data follows gaussian distribution"""
    # usage: df_gaussian_checks(df, 'col_name')
    # input: df_name - pandas DataFrame, col_name - column name to check for normality
    # output: Shapiro-Wilk test statistic and p-value, Q-Q plot
    data = df_name[col_name].dropna()
    
    # shapiro-wilk test
    stat, p_value = stats.shapiro(data)
    print(f"Shapiro-Wilk test for {col_name}:")
    print(f"Statistic: {stat:.4f}, p-value: {p_value:.4f}")
    
    # q-q plot
    fig, ax = plt.subplots(figsize=(8, 6))
    stats.probplot(data, dist="norm", plot=ax)
    plt.title(f'Q-Q Plot for {col_name}')
    plt.show()
    
    return stat, p_value


def df_calc_conf_interval(moe_vals: dict, mean_val):
    """calculate confidence interval"""
    # usage: df_calc_conf_interval({'margin_of_error': 1.96}, mean_val=50)
    # input: moe_vals - dictionary with margin_of_error key, mean_val - mean of the data
    # output: dictionary with lower, upper, and mean values
    lower_bound = mean_val - moe_vals['margin_of_error']
    upper_bound = mean_val + moe_vals['margin_of_error']

    return {'lower': lower_bound, 'upper': upper_bound, 'mean': mean_val}


def df_calc_moe(stderr_val, z_score_cl):
    """calculate margin of error"""
    # usage: df_calc_moe(stderr_val=2.5, z_score_cl=1.96)
    # input: stderr_val - standard error value, z_score_cl - z-score for confidence level
    # output: margin of error value
    margin_of_error = z_score_cl * stderr_val

    return {'margin_of_error': margin_of_error}


def df_calc_stderr(df_name, col_z, stddev_val):
    """calculate standard error"""
    # usage: df_calc_stderr(df, 'col_name', stddev_val=5.0)
    # input: df_name - pandas DataFrame, col_z - column name for standard error calculation, stddev_val - standard deviation of the data
    # output: standard error value
    n = len(df_name[col_z].dropna())
    stderr = stddev_val / np.sqrt(n)

    return stderr


def df_calc_zscore(df_name, col_z, confidence_levels, mean_val, stddev_val):
    """calculate z-score for given confidence level"""
    # usage: df_calc_zscore(df, 'col_name', confidence_levels=95, mean_val=50, stddev_val=5.0)
    # input: df_name - pandas DataFrame, col_z - column name for z-score calculation, confidence_levels - confidence level percentage, mean_val - mean of the data, stddev_val - standard deviation of the data
    # output: z-score value
    alpha = 1 - confidence_levels / 100
    z_score = stats.norm.ppf(1 - alpha/2)

    return z_score


def df_residual_analysis(df_name, col_actual, col_predicted):
    """perform residual analysis"""
    # usage: df_residual_analysis(df, 'actual_col', 'predicted_col')
    # input: df_name - pandas DataFrame, col_actual - actual values column name, col_predicted - predicted values column name
    # output: residuals and residual plots
    df_name['residuals'] = df_name[col_actual] - df_name[col_predicted]
    
    # plot residuals
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df_name[col_predicted], df_name['residuals'])
    ax.axhline(0, color='red', linestyle='--')
    plt.title('Residuals vs Predicted')
    plt.xlabel('Predicted Values')
    plt.ylabel('Residuals')
    plt.show()
    
    # histogram of residuals
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df_name['residuals'], bins=30, edgecolor='k', alpha=0.7)
    plt.title('Histogram of Residuals')
    plt.xlabel('Residuals')
    plt.ylabel('Frequency')
    plt.show()
    
    return df_name['residuals']


def df_vif_calculation(df_name, col_list: list):
    """calculate Variance Inflation Factor (VIF) for multicollinearity check"""
    # usage: df_vif_calculation(df, ['col1', 'col2', 'col3'])
    # input: df_name - pandas DataFrame, col_list - list of numerical column names
    # output: DataFrame with VIF values for each variable
    X = smtools.add_constant(df_name[col_list].dropna())
    vif_data = pd.DataFrame()
    vif_data['Variable'] = X.columns
    vif_data['VIF'] = [smvif(X.values, i) for i in range(X.shape[1])]

    return vif_data


def df_tukey_hsd(df_name, col_group, col_value, alpha=0.05):
    """perform Tukey's HSD test for multiple comparisons"""
    # usage: df_tukey_hsd(df, 'group_col', 'value_col', alpha=0.05)
    # input: df_name - pandas DataFrame, col_group - categorical column name, col_value - numerical column name, alpha - significance level
    # output: Tukey HSD results summary
    tukey = smmulti.pairwise_tukeyhsd(endog=df_name[col_value].dropna(), groups=df_name[col_group].dropna(), alpha=alpha)
    print(tukey.summary())
    
    return tukey


def df_anova_oneway(df_name, col_group, col_value):
    """perform one-way ANOVA test"""
    # usage: df_anova_oneway(df, 'group_col', 'value_col')
    # input: df_name - pandas DataFrame, col_group - categorical column name, col_value - numerical column name
    # output: F-statistic and p-value
    groups = df_name.groupby(col_group)[col_value].apply(list)
    f_stat, p_value = stats.f_oneway(*groups)
    print(f"One-way ANOVA for {col_value} by {col_group}:")
    print(f"F-statistic: {f_stat:.4f}, p-value: {p_value:.4f}")
    
    return f_stat, p_value


def df_anova_twoway(df_name, col_factor1, col_factor2, col_value):
    """perform two-way ANOVA test"""
    # usage: df_anova_twoway(df, 'factor1_col', 'factor2_col', 'value_col')
    # input: df_name - pandas DataFrame, col_factor1 - first categorical column name, col_factor2 - second categorical column name, col_value - numerical column name
    # output: ANOVA table
    formula = f'{col_value} ~ C({col_factor1}) + C({col_factor2}) + C({col_factor1}):C({col_factor2})'
    model = smtools.ols(formula, data=df_name).fit()
    anova_table = smtools.anova_lm(model, typ=2)
    print(anova_table)
    
    return anova_table


def df_chi_square_test(df_name, col1, col2):
    """perform Chi-Square test of independence"""
    # usage: df_chi_square_test(df, 'col1', 'col2')
    # input: df_name - pandas DataFrame, col1 - first categorical column name, col2 - second categorical column name
    # output: chi-square statistic, p-value, degrees of freedom, expected frequencies
    contingency_table = pd.crosstab(df_name[col1], df_name[col2])
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    print(f"Chi-Square Test between {col1} and {col2}:")
    print(f"Chi2 Statistic: {chi2_stat:.4f}, p-value: {p_value:.4f}, Degrees of Freedom: {dof}")
    
    return chi2_stat, p_value, dof, expected


def df_residual_based_filtering(df_name, col_actual, col_predicted, threshold):
    """filter data based on residuals"""
    # usage: df_residual_based_filtering(df, 'actual_col', 'predicted_col', threshold=2.0)
    # input: df_name - pandas DataFrame, col_actual - actual values column name, col_predicted - predicted values column name, threshold - residual threshold
    # output: filtered DataFrame with residuals within the threshold
    df_name['residuals'] = df_name[col_actual] - df_name[col_predicted]
    filtered_df = df_name[np.abs(df_name['residuals']) <= threshold]
    
    return filtered_df


def df_zscore_based_filtering(df_name, x_col, y_col, z_threshold=1.5):
    """filter data based on Z-scores of two columns"""
    # usage: df_zscore_based_filtering(df, 'x_col', 'y_col', z_threshold=1.5)
    # input: df_name - pandas DataFrame, x_col - first numerical column name, y_col - second numerical column name, z_threshold - Z-score threshold
    # output: filtered DataFrame with Z-scores within the threshold for both columns
    data = df_name[[x_col, y_col]].dropna()
    z_scores = stats.zscore(data)
    
    # Filter by Z-score of x_col only (first column of z_scores)
    mask = z_scores[:, 0] < z_threshold  # Only use x_col Z-scores for filtering
    filtered_df = data[mask]
    
    return filtered_df, z_scores


def df_plot_zscores(df, z_scores, x_col, y_col, *save_path):
    """plot Z-scores for two columns"""
    # usage: df_plot_zscores(df, z_scores, 'x_col', 'y_col')
    # or df_plot_zscores(df, z_scores, 'x_col', 'y_col', 'save_path.png')
    # input: df - original pandas DataFrame, z_scores - array of Z-scores, x_col - first numerical column name, y_col - second numerical column name, save_path - optional path to save the plot
    # output: scatter plot of Z-scores for both columns
    plt.figure(figsize=(10, 6))
    plt.scatter(df.index, z_scores[:, 0], label=f'Z-scores {x_col}', alpha=0.5)
    plt.scatter(df.index, z_scores[:, 1], label=f'Z-scores {y_col}', alpha=0.5)
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.axhline(1.5, color='red', linestyle='--', linewidth=1, label='Threshold (1.5)')
    plt.axhline(-1.5, color='red', linestyle='--', linewidth=1)
    plt.title('Z-Scores for Columns')
    plt.xlabel('Index')
    plt.ylabel('Z-Score')
    plt.legend()
    plt.show()
    if save_path:
        plt.savefig(save_path[0])
        plt.close()

    return None


def df_ds_score_filtering(df_name, x_col_name, y_col_name, ds_score_tuner=0.01, log_base=10):
    """filter data based on my custom Data Shadric statistic score filtering"""
    # usage: df_ds_score_filtering(df, 'x_col', 'y_col', ds_score_tuner=0.01, log_base=10)
    # input: df_name - pandas DataFrame, x_col_name - first column name, y_col_name - second column name, ds_score_tuner - score tuning parameter (lower = less filtering/more data retained), log_base - logarithm base for transformation (default: 10)
    # output: filtered DataFrame with scores above the threshold

    # Apply log transformation
    df = df_name.copy() # dataset
    x_max = df[x_col_name].max()
    y_min = df[y_col_name].min()
    x_normalised = (x_max - df[x_col_name]) / (x_max - df[x_col_name].min())
    y_normalised = (df[y_col_name] - y_min) / (df[y_col_name].max() - y_min)
    x_log_normalised = np.log1p(x_normalised) / np.log(log_base)
    y_log_normalised = np.log1p(y_normalised) / np.log(log_base)
    df[f"{x_col_name}_lognorm"] = x_log_normalised
    df[f"{y_col_name}_lognorm"] = y_log_normalised

    # Calculate Z-scores
    ds_score = df[f"{x_col_name}_lognorm"] * df[f"{y_col_name}_lognorm"]

    # Filter by ds-score of x_col only (first column of z_scores)
    print(f"Applying DS-score filtering with threshold tuner: {ds_score_tuner}...")
    mask = ds_score > (ds_score.max() * ds_score_tuner)  # Only use x_col Z-scores for filtering
    df = df[mask]

    # Drop intermediate log-normalised columns
    df = datashadric.dataframing.df_drop_multicol(df, [f"{x_col_name}_lognorm", f"{y_col_name}_lognorm"])

    return df
