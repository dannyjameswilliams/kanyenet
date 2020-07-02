import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Raw data
raw = pd.read_csv("nl_data/raw_nl_data.csv")

# -- Top Words

# Top 10 word entities
top10words = pd.read_csv("nl_data/top10words.csv")
top10words = top10words[["album", "count", "words"]]

albums = top10words.album.unique()
fig, axs = plt.subplots(4,3)
axs = axs.ravel()
for i in np.arange(len(albums)):
    d = top10words[top10words["album"] == albums[i]]
    axs[i] = d[["count", "words"]].plot(kind="pie", y = "count", ax = axs[i], labels=d["words"], legend=None)
    axs[i].set_ylabel("")
    axs[i].set_title(albums[i])
    
plt.show()




# -- Sentiments

# Make new dataframe with all sentence sentiments grouped by album (column)
import ast
def applyf(A):
    n = len(A.sentences)
    df = pd.DataFrame(index=np.arange(0), columns=["sentiment"])
    for i in np.arange(n):
        s  = A.sentences.iloc[i]
        s2 = ast.literal_eval(s[1:(len(s)-1)])
        d = pd.DataFrame.from_records(s2, index=["sentiment"]).T
        df = df.append(d)
    df["album"] = A.album.iloc[0]
    return(df)

sentiment_groups = raw.groupby("album")
sentiment_totals = sentiment_groups.apply(applyf)

g = sns.FacetGrid(sentiment_totals, col='album')
g.map(sns.distplot, "sentiment")
plt.show()

# Sentiment by album
album_sentiment = pd.read_csv("nl_data/album_sentiment.csv")
ax = album_sentiment.plot(kind="bar", x = "album", legend=None)
ax.set_xlabel("Album")
ax.set_ylabel("Mean Sentiment")
