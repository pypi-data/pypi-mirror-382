# -*- coding: utf-8 -*-
"""
datashadric: An Exploratory Data Science Toolkit
==================================================

A Python package providing organized tools for data analysis, machine learning,
statistical testing, visualization, and data manipulation.

Modules:
--------
- mlearning: Machine learning models and evaluation functions
- regression: Regression analysis and diagnostic tools  
- dataframing: Data manipulation and cleaning utilities
- stochastics: Statistical analysis and hypothesis testing
- plotters: Visualization and plotting functions

Basic Usage:
-----------
>>> from datashadric.mlearning import ml_naive_bayes_model
>>> from datashadric.regression import lr_ols_model
>>> from datashadric.dataframing import df_check_na_values
>>> from datashadric.stochastics import df_gaussian_checks
>>> from datashadric.plotters import df_boxplotter
"""

__version__ = "0.1.3"
__author__ = "Paul Namlaomba (GitHub: diversecellar)"
__email__ = "kabwenzenamalomba@gmail.com"

# import main modules for easier access
from . import mlearning
from . import regression
from . import dataframing
from . import stochastics
from . import plotters

# define what gets imported with "from datashadric import *"
__all__ = [
    'mlearning',
    'regression', 
    'dataframing',
    'stochastics',
    'plotters'
]