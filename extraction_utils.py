from psaw import PushshiftAPI
import csv
import os
import pandas as pd
import tqdm
import math
import json
import requests
import itertools
import numpy as np
import time
from datetime import datetime, timedelta

"""
Function to scrape reddit.
"""


def scrape_subreddit(subreddit, file_path='/'):
    api = PushshiftAPI()
    year = datetime.now().year
    data_list = [["isodate", "author", "title", "permalink", "text"]]

    if file_path[-1] == "/": file_path = file_path[:-1]
    filename = f"{file_path}/{subreddit}.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    while year:

        # Set start and end dates for the year
        start_epoch = int(datetime(year, 1, 1).timestamp())
        end_epoch = int(datetime(year, 12, 31).timestamp())

        # Searching subreddit posts
        gen = api.search_submissions(
            subreddit=subreddit,
            after=start_epoch,
            before=end_epoch,
            filter=["author", "title", "permalink", "selftext"]
        )

        # This is used to check whether the generator object has anymore output.
        # If it is False, then we can safely end the scraping process
        post_exists = False

        # We iterate over each object in the generator.
        for item in gen:
            post_exists = True
            data = item[-1]

            # We extract the values and prevent crashes for non-existing ones.
            timestamp = data["created_utc"]
            author = data.get("author", "")
            title = data.get("title", "")
            permalink = data.get("permalink", "")
            text = data.get("selftext", "")

            if permalink != "":
                permalink = "https://www.reddit.com" + permalink

            # We convert the date from a timestamp to ISO format.
            isodate = f"{datetime.fromtimestamp(timestamp):%F %T}"

            data_list.append([isodate, author, title, permalink, text])

        # We save the data list to a CSV file.
        with open(filename, "w", newline="", encoding="utf-8") as csv_file:
            csv.writer(csv_file).writerows(data_list)

        print("Done with subreddit posts. Starting on comments...")

        # Searching subreddit comments
        gen = api.search_comments(
            subreddit=subreddit,
            after=start_epoch,
            before=end_epoch,
            filter=["author", "permalink", "body"]
        )

        # We iterate over each object in the generator.
        for comment in gen:
            post_exists = True
            data = comment[-1]

            # We extract the values and prevent crashes for non-existing ones.
            timestamp = data["created_utc"]
            author = data.get("author", "")
            title = ""
            permalink = data.get("permalink", "")
            body = data.get("body", "")

            if permalink != "":
                permalink = "https://www.reddit.com" + permalink

            # We convert the date from a timestamp to ISO format.
            isodate = f"{datetime.fromtimestamp(timestamp):%F %T}"

            data_list.append([isodate, author, title, permalink, body])

        with open(filename, "w", newline="", encoding="utf-8") as csv_file:
            csv.writer(csv_file).writerows(data_list)

        if not post_exists:
            break

        print(f'YEAR {year} DONE!!!')

        year -= 1


"""
Function to make request to Pushshift
"""
def make_request(uri, max_retries=5):
    def fire_away(uri):
        response = requests.get(uri)
        assert response.status_code == 200
        return json.loads(response.content)

    current_tries = 1
    while current_tries < max_retries:
        try:
            time.sleep(1)
            response = fire_away(uri)
            return response
        except:
            time.sleep(1)
            current_tries += 1
    return fire_away(uri)




"""
Download all comments made anywhere by a given list of authors
"""


def download_author_comments(u_authors, file_path):
    authors_list = []

    for u in tqdm.tqdm(range(len(u_authors))):

        uri = f"https://api.pushshift.io/reddit/comment/search/?author={u_authors[u]}&filter=created_utc,author,subreddit,permalink,body"
        try:
            result = make_request(uri,
                                  max_retries=2)
            authors_list.extend(result['data'])
        except Exception as e:
            print("ERROR :", e)
            pass

    authors_df = pd.DataFrame(authors_list)
    authors_df['isodate'] = authors_df['created_utc'].apply(lambda x: f"{datetime.fromtimestamp(x):%F %T}")
    authors_df.drop(columns=['created_utc'], inplace=True)

    authors_df.to_csv(f'{file_path}_comments.csv', index=False)

    return authors_df


"""
Download all posts made anywhere by a given list of authors
"""


def download_author_posts(u_authors, file_path):
    authors_posts = []

    for u in tqdm.tqdm(range(len(u_authors))):

        uri = f"https://api.pushshift.io/reddit/submission/search/?author={u_authors[u]}&filter=created_utc,author,subreddit,permalink,title,selftext"
        try:
            result = make_request(uri,
                                  max_retries=2)
            authors_posts.extend(result['data'])
        except Exception as e:
            print("ERROR :", e)
            pass

    authors_df = pd.DataFrame(authors_posts)
    authors_df['isodate'] = authors_df['created_utc'].apply(lambda x: f"{datetime.fromtimestamp(x):%F %T}")
    authors_df.drop(columns=['created_utc'], inplace=True)

    authors_df.to_csv(f'{file_path}_posts.csv', index=False)

    return authors_df