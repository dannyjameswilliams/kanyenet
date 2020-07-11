import os
import numpy as np
import pandas as pd
import operator
from functools import reduce

os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")
from clean_nl_data_funs import *

# ==  Remove some small problems, censor, remove duplicates/plurals and reduce to top 10

# -- Top words by album
top15words = pd.read_csv("nl_data/top15words.csv")
top15words = top15words[["album", "count", "words"]]

# love lockdown and love-lockdown are separate
ll_bool = top15words["words"] == "love lockdown"
ll_bool2 = top15words["words"] == "love lock-down"
top15words.loc[ll_bool, "count"] += top15words.loc[ll_bool2, "count"].to_numpy()[0]
drop_ind = top15words.index[ll_bool2]
top15words = top15words.drop(axis="index", labels=drop_ind)
    
# crack music entity is likely a mislabel
cm_bool = top15words["words"] == "crack music nigga"
drop_ind = top15words.index[cm_bool]
top15words = top15words.drop(axis="index", labels=drop_ind)

# Censor curses/remove plurals
censored_words = top15words["words"].apply(censor)
top15words.loc[:, "words"] = censored_words
top10words = top15words.groupby("album").apply(remove_plurals)


# -- Top 10 Words over all albums
from NL_by_song import applyf
raw = pd.read_pickle("nl_data/raw_nl_data")
top15words_all = applyf(raw, nlargest=15)
top10words_all = remove_plurals(top15words_all)
censored_words = top10words_all["words"].apply(censor)
top10words_all.loc[:, "words"] = censored_words

# -- Top 1000 Words over all albums
from NL_by_song import applyf
raw = pd.read_pickle("nl_data/raw_nl_data")
topwords_all = applyf(raw, nlargest=1500)
topwords_all = remove_plurals(topwords_all, top10=False)
censored_words = topwords_all["words"].apply(censor)
topwords_all.loc[:, "words"] = censored_words
top1000words = topwords_all.nlargest(1000, "count")



# -- Same for top sentences 
top15sentences = pd.read_csv("nl_data/top15sentences.csv")
top15sentences = top15sentences[["album", "count", "words"]]

top10sentences = top15sentences.groupby("album").apply(remove_plurals)
censored_words = top10sentences["words"].apply(censor)
top10sentences.loc[:, "words"] = censored_words

# -- Same for bottom sentences
bottom15sentences = pd.read_csv("nl_data/bottom15sentences.csv")
bottom15sentences = bottom15sentences[["album", "count", "words"]]

bottom10sentences = bottom15sentences.groupby("album").apply(remove_plurals)
censored_words = bottom10sentences["words"].apply(censor)
bottom10sentences.loc[:, "words"] = censored_words


# == All sentences and sentiments
raw = pd.read_csv("nl_data/raw_nl_data.csv")
        
# Group by album and use applyf
sentiment_groups = raw.groupby("album")
sentiment_totals = sentiment_groups.apply(sentence_sentiment)
sentiment_totals["sentence"] = [x[1] for x in sentiment_totals.index.values]
sentiment_totals.loc[:,"sentence"] = sentiment_totals["sentence"].str.replace(";", ",")
sentiment_totals = sentiment_totals[sentiment_totals["sentence"].apply(len).values > 6]
sentiment_totals["length"] = sentiment_totals["sentence"].apply(len).values
sentiment_totals["noise"] = np.random.uniform(-1, 1, size=len(sentiment_totals))
sentiment_totals["length_mod"] = (sentiment_totals["length"]/np.max(sentiment_totals["length"]))

# == Create text string with all elements for GPT2 training
from NL_by_song import applyf
raw = pd.read_pickle("nl_data/raw_nl_data")
allwords = applyf(raw, nlargest=0)
censored_words = allwords["words"].apply(censor)
allwords["words"] = censored_words
allwords_string = getallwords(allwords)
    
# == Get mean and SD of sentiment
album_sentiment = raw.groupby("album").apply(mean_sd, 
                                                 name = "song_sentiment") 
album_magnitude = raw.groupby("album").apply(mean_sd,
                                                 name = "song_magnitude" ) 


# == Sorting and Saving

# -- Sort by album in terms of release order
album_sentiment = sort_by_album(album_sentiment)
album_magnitude = sort_by_album(album_magnitude)
top10words = sort_by_album(top10words)
top10sentences = sort_by_album(top10sentences)
bottom10sentences = sort_by_album(bottom10sentences)
sentiment_totals = sort_by_album(sentiment_totals)
raw = sort_by_album(raw)

# -- Save data frames

raw.to_csv("nl_data/raw_nl_data.csv")
top10sentences.to_csv("nl_data/top10sentences.csv", index=False)
bottom10sentences.to_csv("nl_data/bottom10sentences.csv", index=False)
top10words.to_csv("nl_data/top10words.csv", index=False)
album_sentiment.to_csv("nl_data/album_sentiment.csv", index=True)
album_magnitude.to_csv("nl_data/album_magnitude.csv", index=True)
sentiment_totals.to_csv("nl_data/sentiment_totals.csv", index=False)
top10words_all.to_csv("nl_data/top10_overall.csv", index=False)
top1000words.to_csv("nl_data/top1000.csv", index=False)

fname = "nl_data/all_words.txt"
text_file = open(fname, "w")
text_file.write(allwords_string)