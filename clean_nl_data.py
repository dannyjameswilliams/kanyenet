from clean_nl_data_funs import *
import os
import numpy as np
import pandas as pd
import operator
from functools import reduce

os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")


# Top words by album
    top15words = pd.read_csv("nl_data/top15words.csv")
    top15words = top15words[["album", "count", "words"]]

    ## Other general adjustments:

    # love lockdown and love-lockdown are separate
    top15words.loc[top15words["words"] == "love lockdown", "count"] += top15words.loc[top15words["words"] == "love lock-down", "count"].to_numpy()[0]
    drop_ind = top15words.index[top15words["words"] == "love lock-down"]
    top15words = top15words.drop(axis="index", labels=drop_ind)
    
    # crack music entity is likely a mislabel
    drop_ind = top15words.index[top15words["words"] == "crack music nigga"]
    top15words = top15words.drop(axis="index", labels=drop_ind)

    # Censor curse words
    censored_words = top15words["words"].apply(censor)
    top15words["words"] = censored_words

    
    # Remove plurals
    top10words = top15words.groupby("album").apply(remove_plurals)




    # Same for sentences 
    top15sentences = pd.read_csv("nl_data/top15sentences.csv")
    top15sentences = top15sentences[["album", "count", "words"]]

    top10sentences = top15sentences.groupby("album").apply(remove_plurals)
    censored_words = top10sentences["words"].apply(censor)
    top10sentences["words"] = censored_words

    # bottom sentences
    bottom15sentences = pd.read_csv("nl_data/top15words.csv")
    bottom15sentences = bottom15sentences[["album", "count", "words"]]

    bottom10sentences = bottom15sentences.groupby("album").apply(remove_plurals)
    censored_words = bottom10sentences["words"].apply(censor)
    bottom10sentences["words"] = censored_words

    # Top 10 Words overall
    from NL_by_song import applyf
    raw = pd.read_pickle("nl_data/raw_nl_data")
    top15words_all = applyf(raw, nlargest=15)
    top10words_all = remove_plurals(top15words_all)
    censored_words = top10words_all["words"].apply(censor)
    top10words_all.loc[:,"words"] = censored_words

    # Create text string with all elements
    from NL_by_song import applyf
    raw = pd.read_pickle("nl_data/raw_nl_data")
    allwords = applyf(raw, nlargest=0)
    censored_words = allwords["words"].apply(censor)
    allwords["words"] = censored_words
    allwords_string = getallwords(allwords)
    
    # Get mean and SD of sentiment
    album_sentiment = raw.groupby("album").apply(mean_sd, 
                                                 name = "song_sentiment") 
    album_magnitude = raw.groupby("album").apply(mean_sd,
                                                 name = "song_magnitude" ) 


    album_sentiment["album_key"] = pd.Categorical(top10words["album"],
                                                  album_order)
    top10words["album_key"] = pd.Categorical(top10words["album"], 
                                             album_order)
    top10sentences["album_key"] = pd.Categorical(top10sentences["album"],
                                                 album_order)
    bottom10sentences["album_key"] = pd.Categorical(bottom10sentences["album"], 
                                                    album_order)
    album_sentiment["album_key"] = pd.Categorical(album_sentiment["album"],
                                                  album_order)
    album_magnitude["album_key"] = pd.Categorical(album_magnitude["album"],
                                                  album_order)
    

    raw["album_key"] = pd.Categorical(raw["album"], album_order)


    # sort and save all
    raw.sort_values("album_key").to_csv("nl_data/raw_nl_data.csv")
    top10sentences.sort_values("album_key").to_csv("nl_data/top10sentences.csv", index=False)
    bottom10sentences.sort_values("album_key").to_csv("nl_data/bottom10sentences.csv", index=False)
    top10words.sort_values("album_key").to_csv("nl_data/top10words.csv", index=False)
    album_sentiment.sort_values("album_key").to_csv("nl_data/album_sentiment.csv", index=False)
    album_magnitude.sort_values("album_key").to_csv("nl_data/album_magnitude.csv", index=False)
    top10words_all.to_csv("nl_data/top10_overall.csv", index=False)
    
    fname = "nl_data/all_words.txt"
    text_file = open(fname, "w")
    text_file.write(allwords_string)