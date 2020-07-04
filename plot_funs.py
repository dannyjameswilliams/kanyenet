import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from variables import *
import ast

def word_pie_plots():
    # Read data
    top10words = pd.read_csv("nl_data/top10words.csv")
    top10words = top10words[["album", "count", "words"]]

    # Set up variables for plotting
    albums = top10words.album.unique()
    fig, axs = plt.subplots(4,3)
    axs = axs.ravel()
    
    # Loop over each album, plot separate pie chart for each
    for i in np.arange(len(albums)):
        d = top10words[top10words["album"] == albums[i]]
        axs[i] = d[["count", "words"]].plot(kind="pie", y = "count", ax = axs[i], labels=d["words"], legend=None, colors = all_album_cols[i])
        axs[i].set_ylabel("")
        axs[i].set_title(albums[i])

    plt.show()

def sentiment_barplot():
    # Read data
    album_sentiment = pd.read_csv("nl_data/album_sentiment.csv")
    album_magnitude = pd.read_csv("nl_data/album_magnitude.csv")

    # Combine dataframes
    sentiment_magnitude = album_sentiment[["album", "mean"]].rename(columns={"mean":"sentiment"})
    sentiment_magnitude.loc[:,"magnitude"] = album_magnitude.loc[:,"mean"]
    sentiment_magnitude = sentiment_magnitude.melt(id_vars=["album"])

    # Plot with FacetGrid
    g = sns.FacetGrid(sentiment_magnitude, col="variable", sharey="none")
    g2 = g.map(sns.barplot, "album", "value", palette = sns.color_palette(colours), orient = "v", order = sentiment_magnitude.album.unique()).set_titles("{col_name}")
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
    g.map(sns.distplot, "sentiment").set_titles("{col_name}")
    plt.show()