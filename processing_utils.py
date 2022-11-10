# from symspellpy import SymSpell
import pandas as pd
import json
import ast
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from textblob import TextBlob
import sys, os
import numpy as np
import pickle
import nltk
from textblob import Word
nltk.download('punkt')
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
from string import digits
from collections import Counter
import re
import math
from nrclex import NRCLex
import textacy
from empath import Empath
from sklearn.feature_extraction.text import CountVectorizer

# Tonkenizer. Lemmatizer is used here to achieve full morphological analysis and accurately identify the lemma for each word, this is better than simply stemming.
WNL = nltk.WordNetLemmatizer()
lexicon = Empath()
# symsp = SymSpell()

posts_stopwords = ['hi', 'hello', 'everyone', 'thank', 'thankyou'] + list(STOPWORDS)

# function to clean up texts by transforming to lower case, also removing apostrophe
def lowerRep(text):
    text = text.lower()
    text = text.replace("'", "")
    return text


# removing number
def removeNum(text):
    remove_digits = str.maketrans('', '', digits)
    text = text.translate(remove_digits)
    return text


# remove extra chars and stop words
def removeChar(text):
    tokens = nltk.word_tokenize(text)
    text1 = nltk.Text(tokens)
    text_content = [''.join(re.split("[ .,;:!?‘’``''@#$%^_&*()<>{}~\n\t\\\-]", word)) for word in text1]
    return text_content


# remove URLs and images
def removeURL(text):
    if isinstance(text, str):
        text = re.sub(r'http\S+', '', text)
    else:
        text = ""
    return text


# remove ![img] string
def removeImg(text):
    text = re.sub(r'!\[img]\S+', '', text)
    return text


# initial removal of stopwords and empty spaces
def removeSpace(text, stopwords):
    text = [word for word in text if word not in stopwords]
    text = [s for s in text if len(s) != 0]
    return text


# lemmatize
def lemmatize(text):
    text = [WNL.lemmatize(t, 'v') for t in text]
    return text


# tokenize
def tokenize(text):
    tokens = [nltk.word_tokenize(i) for i in text]
    return tokens


# def correct_spelling(sentence):
#     terms = symsp.lookup_compound(sentence,
#                                   max_edit_distance=2)
#     return terms


def get_empath_scores(sentence, normalize=True):
    return lexicon.analyze(sentence, normalize=normalize)


def get_nrc(sentence):
    emotion = NRCLex(" ".join(sentence))
    freq = emotion.affect_frequencies
    if 'anticipation' not in freq:
        freq['anticipation'] = 0
    return freq


def get_pos_words(sentence, tag):
    text = nltk.word_tokenize(" ".join(sentence))
    pos_tagged = nltk.pos_tag(text)
    pos_tagged_words = [word[0] for word in pos_tagged if word[1].startswith(tag)]
    return pos_tagged_words


def get_sr_count(sentence):
    self_reference_words = ["i", "im", "me", "myself", "mine", "my", "self", "m"]
    sr_count = 0
    lst = [1 for word in sentence if word in self_reference_words]
    return sum(lst)


def preprocess_df(df_subreddit, file_name):
    # pre-process to remove duplicate posters, any bots, and posts that have the word quote
    # df_subreddit.reset_index(inplace = True)
    df_subreddit = df_subreddit[df_subreddit['author'] != "[deleted]"]
    df_subreddit = df_subreddit[df_subreddit['body'] != "[deleted]"]
    df_subreddit = df_subreddit[df_subreddit['body'] != "[removed]"]
    df_subreddit["body"].dropna(how='all', inplace=True)
    df_subreddit = df_subreddit.drop_duplicates()

    df_subreddit['processed'] = df_subreddit["body"].apply(lambda x: removeURL(x))
    df_subreddit['processed'] = df_subreddit["processed"].apply(lambda x: removeImg(x))
    df_subreddit['processed'] = df_subreddit["processed"].apply(lambda x: lowerRep(x))
    df_subreddit['processed'] = df_subreddit["processed"].apply(lambda x: removeNum(x))
    df_subreddit['processed'] = df_subreddit["processed"].apply(lambda x: removeChar(x))
    df_subreddit['processed'] = df_subreddit["processed"].apply(lambda x: removeSpace(x, posts_stopwords))
    df_subreddit['processed'] = df_subreddit["processed"].apply(lambda x: lemmatize(x))
    df_subreddit = df_subreddit[df_subreddit["processed"].apply(lambda x: len(x) > 0)]
    df_subreddit["processed"].dropna(how='all', inplace=True)
    df_subreddit.to_csv(f"{file_name}_preprocessed.csv", index=False)

    return df_subreddit

def n_gram_freq(df_subreddit, n):

    posts_content = list(df_subreddit['processed'])
    posts_content = [word for processed in posts_content for word in processed]

    stop_words = posts_stopwords + \
                 ['dont', "don't", "want", "feel", "think", "know", "make", "t", "ive", "doesn't", \
                  "doesn t", "go", "will", "im", "say", "s", "m", "see", "don", "gon", "na"]

    posts_content = [word for word in posts_content if word not in stop_words]

    if n == 1:
        ngrams = [str(u[0]) for u in nltk.ngrams(posts_content, 1)]
        posts_dict_ngram = Counter(ngrams)
        unigram_freq_df = pd.DataFrame(posts_dict_ngram.most_common(), columns=["Unigram", "Frequency"])
        return unigram_freq_df
    elif n==2:
        ngrams = [" ".join(bi) for bi in nltk.ngrams(posts_content, 2)]
        posts_dict_ngram = Counter(ngrams)
        bigram_freq_df = pd.DataFrame(posts_dict_ngram.most_common(), columns=["Bigram", "Frequency"])
        return bigram_freq_df

def get_empath_data(df_subreddit):
    rows = df_subreddit['processed'].apply(lambda x: get_empath_scores(x, True))
    rows = rows.tolist()
    empath_scores = pd.DataFrame.from_dict(rows)
    empath_scores.columns = [f"emp_{col}" for col in empath_scores.columns]
    df_subreddit.reset_index(inplace=True)
    df_subreddit = pd.concat([df_subreddit, empath_scores], axis=1)
    return df_subreddit

def get_nrclex_data(df_subreddit):
    nrc_emotions = df_subreddit['processed'].apply(lambda x: get_nrc(x))
    nrc_emotions = nrc_emotions.tolist()
    nrc_emotions = pd.DataFrame.from_dict(nrc_emotions)
    nrc_emotions.columns = [f"nrc_{em}" for em in nrc_emotions.columns]
    df_subreddit = pd.concat([df_subreddit, nrc_emotions], axis=1)
    df_subreddit.reset_index()
    return df_subreddit

def verb_count(df_subreddit):
    verb_list = df_subreddit['processed'].apply(lambda x: get_pos_words(x, "VB"))
    list_of_verbs = [word for lst in verb_list for word in lst]

    list_synsets = []
    for word in list_of_verbs:
        for synset in wn.synsets(word):
            list_synsets.append(synset.lexname())

    list_synsets = [word[5:] for word in list_synsets if word.startswith("verb")]
    verb_count = Counter(list_synsets)

    verb_df = pd.DataFrame.from_dict(verb_count, orient='index').reset_index()
    verb_df.columns = ["Verb Category", "Count"]
    return verb_df

def noun_count(df_subreddit):
    noun_list = df_subreddit['processed'].apply(lambda x: get_pos_words(x, "NN"))
    list_of_nouns = [word for lst in noun_list for word in lst]

    list_synsets = []
    for word in list_of_nouns:
        for synset in wn.synsets(word):
            list_synsets.append(synset.lexname())

    list_synsets = [word[5:] for word in list_synsets if word.startswith("noun")]
    noun_count = Counter(list_synsets)

    noun_df = pd.DataFrame.from_dict(noun_count, orient='index').reset_index()
    noun_df.columns = ["Noun Category", "Count"]
    return noun_df


def sfa_metrics(df_subreddit):
    sr_count = sum(df_subreddit["body"].apply(lambda x: get_sr_count(x)))
    total_word_count = sum(df_subreddit["body"].apply(lambda x: len(x)))

    # print(f"Self Reference word count : {sr_count}")
    # print(f"Total word count : {total_word_count}")
    # print(f"Percentage of SFA : {sr_count / total_word_count : .2%}")

    metrics = {
        "Self Reference word count": sr_count,
        "Total word count": total_word_count,
        "Percentage of SFA": sr_count / total_word_count
    }
    
    return metrics