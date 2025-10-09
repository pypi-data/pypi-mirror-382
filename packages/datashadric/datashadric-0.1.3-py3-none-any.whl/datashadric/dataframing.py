# -*- coding: utf-8 -*-
"""
Dataframing Functions Module
Comprehensive collection of pandas and numpy utilities for data manipulation and preprocessing
"""

# standard library imports
import re

# third-party data science imports
import pandas as pd
import numpy as np
import unidecode


def df_print_row_and_columns(df_name):
    """print the number of rows and columns in a dataframe"""
    # usage: df_print_row_and_columns(df)
    # input: df_name - pandas DataFrame
    # output: prints number of rows and columns to console
    try:
        df_rows, df_columns = df_name.shape
    except Exception as e:
        df_rows, df_columns = df_name.to_frame().shape
    print("rows = {}".format(df_rows))
    print("columns = {}".format(df_columns))


def df_get_count_on_axis(df_name, axis: int):
    """get the number of rows or columns in a dataframe"""
    # usage: df_get_count_on_axis(df, axis=0) for rows or df_get_count_on_axis(df, axis=1) for columns
    # input: df_name - pandas DataFrame, axis - 0 for rows, 1 for columns
    # output: number of rows or columns in the DataFrame
    try:
        df_rows, df_columns = df_name.shape
    except Exception as e:
        df_rows, df_columns = df_name.to_frame().shape

    return df_rows if axis == 0 else df_columns


def df_check_na_values(df_name, *args):
    """check for missing values in dataframe columns"""
    # usage: df_check_na_values(df) or df_check_na_values(df, ['col1', 'col2'])
    # input: df_name - pandas DataFrame, args - optional list of column names to check for missing values
    # output: boolean DataFrame indicating missing values
    if not args:
        df_na = df_name.isna()
        mask = df_na == True
        masked = df_na[mask]
    else:
        df_na = df_name.isna()
        try:
            column_names = [arg for arg in args[0] if (isinstance(arg, str) and isinstance(args[0], list))]
        except Exception as e:
            print("need to be list of str type for args")
        for column in column_names:
            mask = df_na[column] == True
            masked = df_na[mask]
    print(masked)

    return df_name.isna()


def df_drop_na(df_name, ax: int):
    """drop missing values along specified axis"""
    # usage: df_drop_na(df, ax=0) # ax=0 for rows, ax=1 for columns
    if ax in [0, 1]:
        df_na_out = df_name.dropna(axis=ax)
        return df_na_out


def df_datetime_converter(df_name, col_datetime_lookup='date'):
    """convert columns containing date information to datetime format"""
    # usage: df_datetime_converter(df, 'date') or df_datetime_converter(df) 
    # defaults to all columns with 'date' in their name string
    # input: df_name - pandas DataFrame, col_datetime_lookup - substring to identify date columns
    # output: DataFrame with specified columns converted to datetime format
    for column in df_name.columns.tolist():
        if str(col_datetime_lookup) in str(column):
            print("yes")
            df_name[column] = pd.to_datetime(df_name[column])

    return df_name


def df_explore_unique_categories(df_name, col):
    """print a dataframe with unique categories for each categorical variable"""
    # usage: df_explore_unique_categories(df, 'col_name')
    # input: df_name - pandas DataFrame, col - column name to explore
    # output: DataFrame with unique values in specified column
    df_col_unique = df_name.drop_duplicates(subset=col, keep='first')

    return df_col_unique[col]


def df_mask_with_list(df, df_col, list_comp: list, mask_type: int):
    """mask dataframe with list comparison. mask_type: 0 for isin, 1 for not isin"""
    # usage: df_mask_with_list(df, 'col_name', ['val1', 'val2'], mask_type=0)
    # input: df - pandas DataFrame, df_col - column name to apply mask on, list_comp - list of values for comparison, mask_type - 0 for isin, 1 for not isin
    # output: masked DataFrame
    if mask_type == 0:
        mask = df[df_col].isin(list_comp)
    else:
        mask = ~df[df_col].isin(list_comp)

    return df[mask]


def df_groupby_mask_operate(df, col_name_masker: str, col_name_operate: str, *args):
    """group by and perform operations on masked data"""
    # usage: df_groupby_mask_operate(df, 'col_groupby', 'col_operate', 'mean')
    # input: df - pandas DataFrame, col_name_masker - column name to group by, col_name_operate - column name to perform operation on, args - operation to perform (e.g., 'mean', 'sum')
    # output: DataFrame with grouped statistics
    grouped = df.groupby(col_name_masker)[col_name_operate]
    if args:
        return grouped.agg(args[0])
    
    return grouped.describe()


def df_cross_corr_check(df_name, cols_y: list, cols_x: list):
    """check cross-correlation between y and x variables"""
    # usage: df_cross_corr_check(df, ['col_y1', 'col_y2'], ['col_x1', 'col_x2'])
    # input: df_name - pandas DataFrame, cols_y - list of y variable column names, cols_x - list of x variable column names
    # output: DataFrame with cross-correlation matrix
    correlation_matrix = df_name[cols_y + cols_x].corr()

    return correlation_matrix.loc[cols_y, cols_x]


def df_class_balance(df_filtered):
    """check class balance in filtered dataframe"""
    # usage: df_class_balance(df_filtered)
    # input: df_filtered - pandas DataFrame with categorical variables
    # output: DataFrame with counts and percentages of each class
    value_counts = df_filtered.value_counts()
    percentages = df_filtered.value_counts(normalize=True) * 100
    balance_df = pd.DataFrame({
        'Count': value_counts,
        'Percentage': percentages
    })
    return balance_df


def df_drop_dupes(df, col_dupes: int, *args):
    """drop duplicate rows based on specified columns"""
    # usage: df_drop_dupes(df) or df_drop_dupes(df, ['col1', 'col2'])
    # input: df - pandas DataFrame, col_dupes - 0 to drop duplicates based on all columns, 1 to drop based on specified columns in args
    # output: DataFrame with duplicates removed
    if args:
        subset_cols = args[0] if isinstance(args[0], list) else [args[0]]
        return df.drop_duplicates(subset=subset_cols, keep='first')
    
    return df.drop_duplicates(keep='first')


def df_drop_col(df, col_name: str):
    """drop specified column from dataframe"""
    # usage: df_drop_col(df, 'col_name')
    # input: df - pandas DataFrame, col_name - column name to drop
    # output: DataFrame with specified column removed
    if col_name in df.columns:
        print(f"Dropping Column: {col_name} at index {df.columns.get_loc(col_name)}")
        return df.drop(columns=[col_name])
    
    return df


def df_drop_multicol(df, col_names: list):
    """drop specified columns from dataframe"""
    # usage: df_drop_multicol(df, ['col1', 'col2'])
    # input: df - pandas DataFrame, col_names - list of column names to drop
    # output: DataFrame with specified columns removed
    cols_to_drop = [col for col in col_names if col in df.columns]
    if cols_to_drop:
        for col_name in cols_to_drop:
            print(f"Dropping Column: {col_name} at index {df.columns.get_loc(col_name)}")
        return df.drop(columns=cols_to_drop)

    return df
 

def df_corr_check(df_name, col_y, col_x):
    """check correlation between two variables"""
    # usage: df_corr_check(df, 'col_y', 'col_x')
    # input: df_name - pandas DataFrame, col_y - first variable column name, col_x - second variable column name
    # output: correlation coefficient between the two variables
    correlation = df_name[[col_y, col_x]].corr().iloc[0, 1]

    return correlation


def df_head(df_name, head_num: int):
    """display first n rows of dataframe"""
    # usage: df_head(df, head_num=5)
    # input: df_name - pandas DataFrame, head_num - number of rows to display
    # output: first n rows of the DataFrame
    return df_name.head(head_num)


def df_one_hot_enconding(df_name, col_name, *binary_bool: bool):
    """perform one-hot encoding on categorical variables"""
    # usage: df_one_hot_enconding(df, 'col_name', True) for binary encoding
    # input: df_name - pandas DataFrame, col_name - column name to encode, binary_bool - optional boolean for binary encoding (True for binary, False for full one-hot)
    # output: DataFrame with one-hot encoded columns
    if binary_bool and binary_bool[0]:
        # binary encoding
        encoded_df = pd.get_dummies(df_name[col_name], prefix=col_name, drop_first=True)
    else:
        # full one-hot encoding
        encoded_df = pd.get_dummies(df_name[col_name], prefix=col_name)
    
    # combine with original dataframe
    result_df = pd.concat([df_name.drop(columns=[col_name]), encoded_df], axis=1)

    return result_df


def df_info_dtypes(df_name, *args):
    """display dataframe info and data types"""
    # usage: df_info_dtypes(df, "v"") or df_info_dtypes(df) "v for detailed info"
    # input: df_name - pandas DataFrame
    # output: prints dataframe info and data types to console, still returns data types for further use
    if args:
        if str(args[0])[:1].lower() == "v":
            print("Detailed DataFrame Info:")
            print(df_name.info(verbose=True, null_counts=True))
            print("\nDataFrame Data Types:")
            print(df_name.dtypes)
        else:
            print("\033[91mNB: Only valid arg is 'v' for verbose info\033[0m")
            print("\033[96mNB: Dataframe Data Types still returned\033[0m")

    return df_name.dtypes


def df_column_nms(df_name, *args):
    """get column names of dataframe"""
    # usage: df_column_nms(df, "v") or df_column_nms(df) "v to print columns"
    # input: df_name - pandas DataFrame
    # output: list of column names, print to console
    if args: 
        if str(args[0])[:1].lower() == "v":
            print("DataFrame Columns:")
            print(list(df_name.columns))
        else:
            print("\033[91mNB: Only valid arg is 'v' for verbose info\033[0m")
            print("\033[96mNB: Dataframe Columns still returned\033[0m")

    return list(df_name.columns)


def remove_whitespace(str_target: str):
    """remove whitespace from string"""
    # usage: remove_whitespace(' some text ')
    # input: str_target - input string
    # output: string with whitespace removed
    return str_target.replace(' ', '')


def remove_unicode(str_target: str):
    """remove unicode characters from string"""
    # usage: remove_unicode('café')
    # input: str_target - input string
    # output: string with unicode characters replaced by closest ASCII equivalent
    try:
        clean_string = unidecode.unidecode(str_target)
        return clean_string
    except Exception as e:
        print(f"Error cleaning unicode: {e}")
        return str_target
    

def degree_symbol_parse(str_target: str):
    """replace '90deg' with '90°'"""
    # usage: degree_symbol_parse('Turn 90deg to the right')
    # input: str_target - input string
    # output: string with 'deg' replaced by '°'
    clean_string = re.sub(r'(\d+)deg\b', r'\1°', str_target)

    return clean_string


def df_standardize_colnames(df_name):
    """standardize dataframe column names to lowercase with underscores"""
    # usage: df_standardize_colnames(df)
    # input: df_name - pandas DataFrame
    # output: DataFrame with standardized column names
    df_name.columns = [col.lower().replace(' ', '_') for col in df_name.columns]

    return df_name


def df_move_col_to_pos(df, col_name: str, pos: int):
    """move specified column to given position in dataframe"""
    # usage: df_move_col_to_pos(df, 'col_name', 0) # moves 'col_name' to first position
    # input: df - pandas DataFrame, col_name - column name to move, pos - target position index
    # output: DataFrame with column moved to specified position
    if col_name in df.columns:
        cols = list(df.columns)
        cols.insert(pos, cols.pop(cols.index(col_name)))
        return df[cols]
    
    return df


def df_rename_col(df, col_old_name: str, col_new_name: str):
    """rename specified column in dataframe"""
    # usage: df_rename_col(df, 'old_name', 'new_name')
    # input: df - pandas DataFrame, col_old_name - current column name, col_new_name - new column name
    # output: DataFrame with renamed column
    if col_old_name in df.columns:
        return df.rename(columns={col_old_name: col_new_name})
    
    return df


def df_rename_multicol(df, col_rename_dict: dict):
    """rename multiple columns in dataframe"""
    # usage: df_rename_multicol(df, {'old_name1': 'new_name1', 'old_name2': 'new_name2'})
    # input: df - pandas DataFrame, col_rename_dict - dictionary mapping old column names to new column names
    # output: DataFrame with renamed columns
    valid_renames = {old: new for old, new in col_rename_dict.items() if old in df.columns}
    if valid_renames:
        return df.rename(columns=valid_renames)
    
    return df


def df_replace_in_col(df, col_name: str, to_replace, value):
    """replace values in specified column of dataframe"""
    # usage: df_replace_in_col(df, 'col_name', 'old_value', 'new_value')
    # input: df - pandas DataFrame, col_name - column name to operate on, to_replace - value to replace, value - new value
    # output: DataFrame with values replaced in specified column
    if col_name in df.columns:
        df[col_name] = df[col_name].replace(to_replace, value)
        return df
    
    return df


def df_replace_in_multicol(df, col_replace_dict: dict):
    """replace multiple values in specified columns of dataframe"""
    # usage: df_replace_multicol(df, {'col_name1': {'old_value1': 'new_value1'}, 'col_name2': {'old_value2': 'new_value2'}})
    # input: df - pandas DataFrame, col_replace_dict - dictionary mapping column names to dictionaries of values to replace
    # output: DataFrame with values replaced in specified columns
    for col_name, replacements in col_replace_dict.items():
        if col_name in df.columns:
            df[col_name] = df[col_name].replace(replacements)
    
    return df


def df_convert_col_type(df, col_name: str, new_type):
    """convert specified column to new data type"""
    # usage: df_convert_col_type(df, 'col_name', 'float') or df_convert_col_type(df, 'col_name', float)
    # input: df - pandas DataFrame, col_name - column name to convert, new_type - target data type (str or type)
    # output: DataFrame with converted column
    if col_name in df.columns:
        try:
            df[col_name] = df[col_name].astype(new_type)
        except Exception as e:
            print(f"Error converting column {col_name} to {new_type}: {e}")
    
    return df


def df_convert_multicol_type(df, col_type_dict: dict):
    """convert multiple columns to new data types"""
    # usage: df_convert_multicol_type(df, {'col_name1': 'float', 'col_name2': 'int'})
    # input: df - pandas DataFrame, col_type_dict - dictionary mapping column names to target data types (str or type)
    # output: DataFrame with converted columns
    for col_name, new_type in col_type_dict.items():
        if col_name in df.columns:
            try:
                df[col_name] = df[col_name].astype(new_type)
            except Exception as e:
                print(f"Error converting column {col_name} to {new_type}: {e}")
    
    return df


def df_fill_na_with_value(df, col_name: str, fill_value):
    """fill missing values in specified column with given value"""
    # usage: df_fill_na_with_value(df, 'col_name', 0)
    # input: df - pandas DataFrame, col_name - column name to operate on, fill_value - value to fill missing values with
    # output: DataFrame with missing values filled in specified column
    if col_name in df.columns:
        df[col_name] = df[col_name].fillna(fill_value)
        return df
    
    return df


def df_fill_na_with_method(df, col_name: str, method: str):
    """fill missing values in specified column using given method"""
    # usage: df_fill_na_with_method(df, 'col_name', 'ffill') or df_fill_na_with_method(df, 'col_name', 'bfill')
    # input: df - pandas DataFrame, col_name - column name to operate on, method - method to use ('ffill' for forward fill, 'bfill' for backward fill)
    # output: DataFrame with missing values filled in specified column
    if col_name in df.columns:
        if method in ['ffill', 'bfill']:
            df[col_name] = df[col_name].fillna(method=method)
        else:
            print("Invalid method. Use 'ffill' or 'bfill'.")
        return df
    
    return df


def df_fill_na_with_mean(df, col_name: str):
    """fill missing values in specified column with column mean"""
    # usage: df_fill_na_with_mean(df, 'col_name')
    # input: df - pandas DataFrame, col_name - column name to operate on
    # output: DataFrame with missing values filled with column mean in specified column
    if col_name in df.columns:
        mean_value = df[col_name].mean()
        df[col_name] = df[col_name].fillna(mean_value)
        return df
    
    return df


def df_fill_na_with_median(df, col_name: str):
    """fill missing values in specified column with column median"""
    # usage: df_fill_na_with_median(df, 'col_name')
    # input: df - pandas DataFrame, col_name - column name to operate on
    # output: DataFrame with missing values filled with column median in specified column
    if col_name in df.columns:
        median_value = df[col_name].median()
        df[col_name] = df[col_name].fillna(median_value)
        return df
    
    return df


def df_fill_na_with_mode(df, col_name: str):
    """fill missing values in specified column with column mode"""
    # usage: df_fill_na_with_mode(df, 'col_name')
    # input: df - pandas DataFrame, col_name - column name to operate on
    # output: DataFrame with missing values filled with column mode in specified column
    if col_name in df.columns:
        mode_value = df[col_name].mode()[0]
        df[col_name] = df[col_name].fillna(mode_value)
        return df
    
    return df


def df_describe(df_name, *args):
    """generate descriptive statistics of dataframe"""
    # usage: df_describe(df) or df_describe(df, ['col1', 'col2'])
    # input: df_name - pandas DataFrame, args - optional list of column names to describe
    # output: DataFrame with descriptive statistics
    if args:
        subset_cols = args[0] if isinstance(args[0], list) else [args[0]]
        return df_name[subset_cols].describe()
    
    return df_name.describe()


def df_to_numpy(df_name, *args):
    """convert dataframe to numpy array"""
    # usage: df_to_numpy(df) or df_to_numpy(df, ['col1', 'col2'])
    # input: df_name - pandas DataFrame, args - optional list of column names to convert
    # output: numpy array of dataframe values
    if args:
        subset_cols = args[0] if isinstance(args[0], list) else [args[0]]
        return df_name[subset_cols].to_numpy()
    
    return df_name.to_numpy()


def df_from_numpy(np_array, col_names: list):
    """create dataframe from numpy array"""
    # usage: df_from_numpy(np_array, ['col1', 'col2'])
    # input: np_array - numpy array, col_names - list of column names for dataframe
    # output: pandas DataFrame created from numpy array
    return pd.DataFrame(np_array, columns=col_names)


def df_concat(df_list: list, axis: int):
    """concatenate list of dataframes along specified axis"""
    # usage: df_concat([df1, df2], axis=0) # axis=0 for rows, axis=1 for columns
    # input: df_list - list of pandas DataFrames, axis - axis to concatenate along (0 for rows, 1 for columns)
    # output: concatenated DataFrame
    if all(isinstance(df, pd.DataFrame) for df in df_list):
        return pd.concat(df_list, axis=axis)
    else:
        print("All items in df_list must be pandas DataFrames.")
        return None
    

def df_merge(df_left, df_right, on: str, how: str):
    """merge two dataframes on specified column with given method"""
    # usage: df_merge(df1, df2, 'col_name', 'inner') # how can be 'inner', 'outer', 'left', 'right'
    # input: df_left - left pandas DataFrame, df_right - right pandas DataFrame, on - column name to merge on, how - merge method
    # output: merged DataFrame
    if how in ['inner', 'outer', 'left', 'right']:
        return pd.merge(df_left, df_right, on=on, how=how)
    else:
        print("Invalid merge method. Use 'inner', 'outer', 'left', or 'right'.")
        return None
    

def df_sample(df_name, n: int, replace: bool = False, random_state: int = None):
    """randomly sample n rows from dataframe"""
    # usage: df_sample(df, n=10, replace=False, random_state=42)
    # input: df_name - pandas DataFrame, n - number of rows to sample, replace - whether to sample with replacement, random_state - random seed for reproducibility
    # output: sampled DataFrame
    return df_name.sample(n=n, replace=replace, random_state=random_state)


def df_sort_by_col(df, col_name: str, ascending: bool = True):
    """sort dataframe by specified column"""
    # usage: df_sort_by_col(df, 'col_name', ascending=True)
    # input: df - pandas DataFrame, col_name - column name to sort by, ascending - whether to sort in ascending order
    # output: sorted DataFrame
    if col_name in df.columns:
        return df.sort_values(by=col_name, ascending=ascending)
    
    return df


def df_reset_index(df, drop: bool = True):
    """reset dataframe index"""
    # usage: df_reset_index(df, drop=True)
    # input: df - pandas DataFrame, drop - whether to drop the old index
    # output: DataFrame with reset index
    return df.reset_index(drop=drop)


def df_set_index(df, col_name: str):
    """set specified column as dataframe index"""
    # usage: df_set_index(df, 'col_name')
    # input: df - pandas DataFrame, col_name - column name to set as index
    # output: DataFrame with specified column as index
    if col_name in df.columns:
        return df.set_index(col_name)
    
    return df


def df_append_row(df, row_data: dict):
    """append a new row to dataframe"""
    # usage: df_append_row(df, {'col1': val1, 'col2': val2})
    # input: df - pandas DataFrame, row_data - dictionary mapping column names to values for the new row
    # output: DataFrame with new row appended
    return df.append(row_data, ignore_index=True)


def df_apply_function(df, col_name: str, func):
    """apply a function to specified column of dataframe"""
    # usage: df_apply_function(df, 'col_name', lambda x: x*2)
    # input: df - pandas DataFrame, col_name - column name to apply function on, func - function to apply
    # output: DataFrame with function applied to specified column
    if col_name in df.columns:
        df[col_name] = df[col_name].apply(func)
        return df
    
    return df

def df_remove_rows_by_condition(df, col_name: str, condition):
    """remove rows from dataframe based on condition in specified column"""
    # usage: df_remove_rows_by_condition(df, 'col_name', lambda x: x < 0)
    # input: df - pandas DataFrame, col_name - column name to apply condition on, condition - function that returns boolean
    # output: DataFrame with rows removed based on condition
    if col_name in df.columns:
        mask = df[col_name].apply(condition)
        return df[~mask]
    
    return df


def df_rename_index(df, new_index_name: str):
    """rename dataframe index"""
    # usage: df_rename_index(df, 'new_index_name')
    # input: df - pandas DataFrame, new_index_name - new name for the index
    # output: DataFrame with renamed index
    df.index.name = new_index_name
    return df


def df_get_index_name(df):
    """get the name of the dataframe index"""
    # usage: df_get_index_name(df)
    # input: df - pandas DataFrame
    # output: name of the index
    return df.index.name


def df_get_column_name_by_index(df, index: int):
    """get column name by index"""
    # usage: df_get_column_name_by_index(df, 0)
    # input: df - pandas DataFrame, index - column index
    # output: column name at specified index
    if 0 <= index < len(df.columns):
        return df.columns[index]
    else:
        print("Index out of range.")
        return None
    

def df_get_column_index_by_name(df, col_name: str):
    """get column index by name"""
    # usage: df_get_column_index_by_name(df, 'col_name')
    # input: df - pandas DataFrame, col_name - column name
    # output: index of specified column name
    if col_name in df.columns:
        return df.columns.get_loc(col_name)
    else:
        print("Column name not found.")
        return None
    

def df_get_all_column_names(df):
    """get all column names of dataframe"""
    # usage: df_get_all_column_names(df)
    # input: df - pandas DataFrame
    # output: list of all column names
    return list(df.columns)


def df_get_all_column_indices(df):
    """get all column indices of dataframe"""
    # usage: df_get_all_column_indices(df)
    # input: df - pandas DataFrame
    # output: list of all column indices
    return list(range(len(df.columns)))