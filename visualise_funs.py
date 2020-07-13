import numpy as np
import pandas as pd
import seaborn as sns
import os
import matplotlib.image as im
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as patches
from variables import *
import ast
from PIL import Image

def word_pie_plots():
    # Read data
    top10words = pd.read_csv("nl_data/top10words.csv")
    top10words = top10words[["album", "count", "words"]]
    top10words["album_key"] = pd.Categorical(top10words["album"], album_order)
    top10words = top10words.sort_values(by=["album_key", "count"], ascending=[True, False])
    
    # Set up variables for plotting
    albums = top10words.album.unique()
    dpi=96
    fig, axs = plt.subplots(6,2, figsize = (700/dpi, 1680/dpi))
    axs = axs.ravel()
    
    # Loop over each album, plot separate pie chart for each
    for i in np.arange(len(albums)):
        
        # Plot Pie chart
        d = top10words[top10words["album"] == albums[i]]
        axs[i] = d[["count", "words"]].plot(kind="pie", y = "count", ax = axs[i], labels=d["words"], legend=None, colors = all_album_cols[i], startangle = 180, textprops={'fontsize': 12})
        axs[i].set_ylabel("")
        #axs[i].set_title(albums[i], fontweight = "bold", fontfamily="serif")

        # Read image (saved in variables.py)
        im_fn = "images/album_covers/" + album_filenames[i]
        image = plt.imread(im_fn)
        
        # Create circle patch centred in middle
        circle = patches.Circle((0,0), 0.8, fc = "white")
        axs[i].add_patch(circle)
        
        # Add image on top of plot
        zoom = 0.35
        if i == 6: zoom +=  0.1
        imagebox = OffsetImage(image, zoom=zoom, clip_path=circle, zorder=-10, alpha=0.67)
        ab = AnnotationBbox(imagebox, (0,0), xycoords='data', pad=0, frameon=False)
        axs[i].add_artist(ab)

    axs[len(albums)].axis("off")
    axs[len(albums)].grid("off")
    
        
    #fig.suptitle("Top 10 Entities by Album", fontweight="bold")
    plt.savefig("images/top10words_notitles_raw.png", 
                quality = 100
               )  


def sentiment_errorplot():
    # Read data
    album_sentiment = pd.read_csv("nl_data/album_sentiment.csv")
    album_magnitude = pd.read_csv("nl_data/album_magnitude.csv")
    album_sentiment["type"] = "sentiment" 
    album_magnitude["type"] = "magnitude" 
    
    
    # Combine dataframes
    sentiment_magnitude = pd.concat([album_sentiment, album_magnitude])
    sentiment_magnitude = sentiment_magnitude[["album", "mean", "sd", "type"]]
    
    figs, axs = plt.subplots(2, 1, sharex=True)
    axs[0].bar(x = album_sentiment["album"], 
               height = album_sentiment["mean"],
               ecolor = colours,
               color = [a + (0.6,) for a in colours_rgb],
               linewidth = 0,
               yerr = album_sentiment["sd"])
    axs[0].scatter(album_sentiment["album"], 
                album_sentiment["mean"], 
                color = colours_rgb,
                marker='o')
    axs[0].set_ylabel("Sentiment")
    axs[1].bar(x = album_magnitude["album"], 
               height = album_magnitude["mean"],
               ecolor = colours,
               color = [a + (0.6,) for a in colours_rgb],
               linewidth = 0,
               yerr = album_magnitude["sd"])
    axs[1].scatter(album_magnitude["album"], 
                album_magnitude["mean"], 
                color = colours_rgb,
                marker='o')
    axs[1].set_ylabel("Magnitude")
    
    for ax in axs:
        ax.tick_params(labelrotation=90)
        ax.grid(False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        #ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.box(on=None)
    plt.show()
    

def sentiment_density_plot():
    
    sentiment_totals = pd.read_csv("nl_data/sentiment_totals.csv")
    
    g = sns.FacetGrid(sentiment_totals, col='album', hue = "album", palette = sns.color_palette(colours), col_wrap = 6)
    g.map(sns.distplot, "sentiment").set_titles("{col_name}", fontweight="bold")
    plt.subplots_adjust(top=0.9)
    g = g.fig.suptitle("Sentiment Density", fontweight="bold")

    plt.show()
    
    ax = sns.distplot(sentiment_totals["sentiment"].values, bins=10)
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Density")
    plt.show()
    

from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
def plot_wordcloud():
    
    kanye_mask = np.array(Image.open("images/kanye_mask1.jpg"))
    kanye_mask[kanye_mask > 245] = 255
    #kanye_mask[kanye_mask == 0] = 255
    
    kanye_colouring = ImageColorGenerator(kanye_mask)
    
    removals = ["bitch", "ass", "dick", "motherf***er", "pussy", "bitches"]
    for word in removals: stopwords.append(word)
    
    text = open(os.path.join("nl_data/all_words.txt")).read()
    wc = WordCloud(background_color="white", 
                   stopwords = stopwords,
                   mask = kanye_mask,
                   include_numbers = True,
                   width = 200,
                   height = 300
                  ).generate(text)
    
    plt.figure(figsize=(20,24))
    plt.imshow(wc.recolor(color_func=kanye_colouring), interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
    