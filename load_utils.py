
import pandas as pd

"""
Load and process posts and comments from a subreddit
"""


def get_processed_df(file_path):
    df_subreddit = pd.read_csv(f"{file_path}.csv")
    df_subreddit = df_subreddit[df_subreddit['author'] != "[deleted]"]
    df_subreddit = df_subreddit[df_subreddit['text'] != "[deleted]"]
    df_subreddit = df_subreddit[df_subreddit['text'] != "[removed]"]
    df_subreddit["text"].fillna(" ", inplace=True)
    df_subreddit = df_subreddit.drop_duplicates()

    return df_subreddit


"""
Get list of unique authors posting at a given subreddit
"""


def get_unique_authors(df_subreddit):
    # Only take users who posted more than once
    repeating = df_subreddit[df_subreddit.duplicated(['author'], keep=False)]
    # Get rid of deleted users
    repeating = repeating[repeating.author != 'None']
    u_authors = list(repeating.author.unique())

    print("Number of unique authors :", len(u_authors))
    return u_authors


"""
Given a subreddit, get posts and comments made by authors on this subreddit.

"""


def get_author_posts_df(sub):
    df_subreddit = pd.DataFrame()

    comment_file = f"{sub}/{sub}_comments.csv"
    posts_file = f"{sub}/{sub}_posts.csv"

    df = pd.read_csv(comment_file)
    df = df[['isodate', 'subreddit', 'author', 'body']]
    df['source'] = sub
    df_subreddit = pd.concat([df_subreddit, df])

    df = pd.read_csv(posts_file)
    df = df.rename({'selftext': 'body'}, axis=1)
    df = df[['isodate', 'subreddit', 'author', 'body']]
    df['source'] = sub
    df_subreddit = pd.concat([df_subreddit, df])

    df_subreddit['isodate'] = pd.to_datetime(df_subreddit["isodate"])

    return df_subreddit


def get_common_authors_posts(df_subreddit, subreddit_list, sub_name):
    # Extract authors posting in subject2 subreddits as well
    df_common = df_subreddit[df_subreddit["subreddit"].isin(subreddit_list)]
    m_authors = list(df_common['author'].unique())
    print("Number of unique authors :", len(m_authors))

    # Extract all posts from these authors
    df_common_author_posts = df_subreddit[df_subreddit["author"].isin(m_authors)]
    df_common_author_posts = df_common_author_posts[df_common_author_posts['author'] != "[deleted]"]
    df_common_author_posts = df_common_author_posts[df_common_author_posts['body'] != "[deleted]"]
    df_common_author_posts = df_common_author_posts[df_common_author_posts['body'] != "[removed]"]
    df_common_author_posts["body"].fillna(" ", inplace=True)

    df_common_author_posts.to_csv(f'{sub_name}/{sub_name}_mentalhealth_common_author_posts.csv', index=False)

    return df_common_author_posts