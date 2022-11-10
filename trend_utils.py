import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import statsmodels.api as sm

def get_time_aggregated_df(df_subreddit, agg_cols):
    groupby_str = f"df_subreddit.groupby(by =[pd.Grouper(key='isodate', axis=0, freq='M')] ).agg("
    for col in agg_cols:
        col_string = f"{col}=('{col}', np.mean),"
        groupby_str += col_string

    groupby_str = groupby_str[:-1]
    groupby_str += ").reset_index()"
    return eval(groupby_str)

def add_freq(idx, freq=None):
    """Add a frequency attribute to idx, through inference or directly.

    Returns a copy.  If `freq` is None, it is inferred.
    """

    idx = idx.copy()
    if freq is None:
        if idx.freq is None:
            freq = pd.infer_freq(idx)
        else:
            return idx
    idx.freq = pd.tseries.frequencies.to_offset(freq)
    if idx.freq is None:
        raise AttributeError('no discernible frequency found to `idx`.  Specify'
                             ' a frequency string with `freq`.')
    return idx

