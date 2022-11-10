from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

posts_stopwords = ['hi', 'hello', 'everyone', 'thank', 'thankyou'] + list(STOPWORDS)
stop_words = posts_stopwords + \
             ['dont', "don't", "want", "feel", "think", "know", "make", "t", "ive", "doesn't", \
              "doesn t", "go", "will", "im", "say", "s", "m", "see", "don", "gon", "na"]

def plot_wordcloud(freq_df, n_gram):
    wc_posts = WordCloud(
            background_color = 'white',
            stopwords = stop_words)
    wc_posts.generate_from_frequencies(dict(zip(freq_df[freq_df.columns[0]], freq_df[freq_df.columns[1]])))

    plt.imshow(wc_posts, interpolation="bilinear")
    plt.axis('off')
    plt.title(f'{n_gram} Wordcloud', loc='center')

def plot_subjectivity(df_subreddit):
    num_bins = 50
    n, bins, patches = plt.hist(df_subreddit.Subjectivity, num_bins, facecolor='blue', alpha=0.5)
    plt.xlabel('Subjectivity')
    plt.ylabel('Count')
    plt.title('Histogram of Subjecticity')
    plt.show()

def plot_polarity(df_subreddit):
    num_bins = 50
    n, bins, patches = plt.hist(df_subreddit.Polarity, num_bins, facecolor='blue', alpha=0.5)
    plt.xlabel('Polarity')
    plt.ylabel('Count')
    plt.title('Histogram of Polarity')
    plt.show()

def plot_empath(mean_df):
    plt.figure(figsize=(50, 20))
    plt.rcParams.update({'font.size': 10})
    mean_df.plot(kind='bar')
    plt.xlabel('Empath categories')
    plt.ylabel('Average normalized value')
    plt.title('Empath categories by normalized value')
    plt.xticks(rotation=90)
    plt.show()

def plot_nrclex(sum_df):
    sum_df.plot(kind='bar')
    plt.xlabel('NRCLex Emotion categories')
    plt.ylabel('Sum of values')
    plt.title('NRCLex Emotion Distribution')
    plt.rcParams.update({'font.size': 5})
    plt.show()

def plot_verb_category(verb_df):
    plt.bar(verb_df["Verb Category"], verb_df['Count'])
    plt.xlabel('Verb Lexname')
    plt.ylabel('Frequency')
    plt.title('Verb Lexname Distribution')
    plt.rcParams.update({'font.size': 10})
    plt.xticks(rotation=90)
    plt.show()

def plot_noun_category(noun_df):
    plt.bar(noun_df["Noun Category"], noun_df['Count'])

    # plt.bar(noun_count.keys(), noun_count.values())
    plt.xlabel('Noun Lexname')
    plt.ylabel('Frequency')
    plt.title('Noun Lexname Distribution')
    plt.rcParams.update({'font.size': 10})
    plt.xticks(rotation=90)
    plt.show()