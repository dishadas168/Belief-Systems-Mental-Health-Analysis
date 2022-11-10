import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from tqdm import tqdm
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
# import seaborn as sns


def get_all_authors(grouped):
    return list(grouped['author'].unique())


"""
Fit a linear model to a time-series data consisting of time and emotion scores.
Positive slope value indicates improvement of the emotion score over time.
"""


def get_slope(X, y):
    X = np.array(X, dtype='float').reshape(-1, 1)
    y = np.array(y.values, dtype='float')
    lm = linear_model.LinearRegression()
    lm.fit(X, y)
    return float(lm.coef_)


"""
Group DF by author and date of posting, 
aggregated by the mean of emotion scores for the day
"""


def get_aggregated_df(df_subreddit, agg_cols):
    groupby_str = f"df_subreddit.groupby(by =['author',pd.Grouper(key='isodate', axis=0, freq='D')] ).agg("
    for col in agg_cols:
        col_string = f"{col}=('{col}', np.mean),"
        groupby_str += col_string

    groupby_str = groupby_str[:-1]
    groupby_str += ").reset_index()"
    return eval(groupby_str)


"""
For every author, get the change in emotion (slope)
"""


def get_authors_change_data(columns, grouped):
    authors_list = []
    all_authors = get_all_authors(grouped)

    for i in tqdm(range(len(all_authors))):
        authors_dict = {}
        author = all_authors[i]

        author_df = grouped[grouped['author'] == author]
        X = author_df['isodate']
        authors_dict['author'] = author

        for col in columns:
            y = author_df[col]
            slope = get_slope(X, y)
            authors_dict[col] = slope

        authors_list.append(authors_dict)

    authors_stats = pd.DataFrame.from_dict(authors_list, orient='columns')
    return authors_stats

def mann_whitney_u_test(sub_df1, sub_df2, alternative = 'two-sided'):
    # perform two-sided test. You can use 'greater' or 'less' for one-sided test
    mannwhitney_dict = {}

    for col in sub_df1.columns[1:]:
        output = stats.mannwhitneyu(x=sub_df1[col], y=sub_df2[col], alternative=alternative)
        mannwhitney_dict[col] = output

    mannwhitney_df = pd.DataFrame.from_dict(mannwhitney_dict, orient='index')
    mannwhitney_df.sort_values(by='pvalue', inplace=True)

    return mannwhitney_df