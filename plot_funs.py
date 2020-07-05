import numpy as np
import pandas as pd
import seaborn as sns
import os
import matplotlib.pyplot as plt
from variables import *
import ast

def word_pie_plots():
    # Read data
    top10words = pd.read_csv("nl_data/top10words.csv")
    top10words = top10words[["album", "count", "words"]]
    top10words["album_key"] = pd.Categorical(top10words["album"], album_order)
    top10words = top10words.sort_values(by=["album_key", "count"], ascending=[True, False])
    
    # Set up variables for plotting
    albums = top10words.album.unique()
    fig, axs = plt.subplots(4,3)
    axs = axs.ravel()
    
    # Loop over each album, plot separate pie chart for each
    for i in np.arange(len(albums)):
        d = top10words[top10words["album"] == albums[i]]
        axs[i] = d[["count", "words"]].plot(kind="pie", y = "count", ax = axs[i], labels=d["words"], legend=None, colors = all_album_cols[i])
        axs[i].set_ylabel("")
        axs[i].set_title(albums[i], fontweight = "bold")
    fig.suptitle("Top 10 Elements by Album", fontweight="bold")
    plt.show()

def word_bar_plots():
    # Read data
    top10words = pd.read_csv("nl_data/top10words.csv")
    top10words = top10words[["album", "count", "words"]]
    top10words["album_key"] = pd.Categorical(top10words["album"], album_order)
    top10words = top10words.sort_values(by=["album_key", "count"], ascending=[True, False])
    
    # Set up variables for plotting
    albums = top10words.album.unique()
    
    # Seaborn FacetGrid for multiple plots
    g = sns.FacetGrid(top10words, col = "album", hue = "album", col_wrap = 6, palette = sns.color_palette(colours), sharex="none", sharey="none")
    g2 = g.map(sns.barplot, "words", "count")
    
    plt.show()
    
def sentiment_barplot():
    # Read data
    album_sentiment = pd.read_csv("nl_data/album_sentiment.csv")
    album_magnitude = pd.read_csv("nl_data/album_magnitude.csv")

    # Combine dataframes
    sentiment_magnitude = album_sentiment[["album", "mean"]].rename(columns={"mean":"Sentiment"})
    sentiment_magnitude.loc[:,"Magnitude"] = album_magnitude.loc[:,"mean"]
    sentiment_magnitude = sentiment_magnitude.melt(id_vars=["album"])
    
    
    # Plot with FacetGrid
    g = sns.FacetGrid(sentiment_magnitude, col="variable", sharey="none")
    g2 = g.map(sns.barplot, "album", "value", palette = sns.color_palette(colours), orient = "v", order = sentiment_magnitude.album.unique()).set_titles("{col_name}", fontweight="bold")
    g2 = g2.set_xticklabels(sentiment_magnitude.album.unique(), rotation=60, horizontalalignment='right')
    plt.show()

    
def sentiment_density_plot():
    # Read raw data
    raw = pd.read_csv("nl_data/raw_nl_data.csv")
    
    # Define function to be applied across albums
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
    
    # Group by album and use applyf
    sentiment_groups = raw.groupby("album")
    sentiment_totals = sentiment_groups.apply(applyf)
    
    # Sort and use FacetGrid to separate and plot
    sentiment_totals["album_key"] = pd.Categorical(sentiment_totals["album"], album_order)
    sentiment_totals = sentiment_totals.sort_values("album_key")
    g = sns.FacetGrid(sentiment_totals, col='album', hue = "album", palette = sns.color_palette(colours), col_wrap = 6)
    g.map(sns.distplot, "sentiment").set_titles("{col_name}", fontweight="bold")
    plt.subplots_adjust(top=0.9)
    g = g.fig.suptitle("Sentiment Density", fontweight="bold")

    plt.show()

def sentiment_song():
    # Read raw data
    raw = pd.read_pickle("nl_data/raw_nl_data")
    song_sentiment = raw[["song", "song_sentiment"]]
    lowest_sentiments = song_sentiment.sort_values("song_sentiment")[0:5]
    lowest_sentiments["id"] = "Bottom 5"
    highest_sentiments = song_sentiment.sort_values("song_sentiment", ascending=False)[0:5]
    highest_sentiments["id"] = "Top 5"
    top5s = pd.concat([highest_sentiments, lowest_sentiments])
      
    fig, axs = plt.subplots(1,2)
    axs = axs.ravel()
    
    axs[0] = lowest_sentiments.plot(kind="bar", y="song_sentiment", ax = axs[0], x = "song", color = scale_cols_blue, legend=None)
    axs[1] = highest_sentiments.plot(kind="bar",  y="song_sentiment", ax = axs[1], x = "song", color = scale_cols_green, legend=None)
       
    plt.show()
    

from wordcloud import WordCloud
from PIL import Image
def plot_wordcloud():
    
    kanye_mask = np.array(Image.open("images/kanye_mask2.png"))
    kanye_mask[kanye_mask > 230] = 255
    kanye_mask[kanye_mask == 0] = 255
    
    text = open(os.path.join("nl_data/all_words.txt")).read()
    wc = WordCloud(background_color="white", stopwords = stopwords, mask=kanye_mask).generate(text)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()