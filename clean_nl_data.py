import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")

import numpy as np
import pandas as pd
import operator
from functools import reduce

def remove_plurals(A, name = "words", top10=True):
    
    substr  = A[name].apply(lambda x: x[0:(len(x)-1)])
    rec = np.empty((0,2), dtype=int)
    for i in np.arange(len(substr)):
        matches = A[name] == substr.iloc[i]
        duplicates = A[name] == A[name].iloc[i]
        if matches.any() and A[name].iloc[i][len(A[name].iloc[i])-1] == "s":
            rec = np.append(rec, [[np.where(matches)[0][0],i]], axis=0)
        elif duplicates.any() and np.where(duplicates)[0][0] != i:
            rec = np.append(rec, [[np.where(duplicates)[0][0],i]], axis=0)
            
    for j in np.arange(np.shape(rec)[0]):
        loc_nonplural = rec[0, 0]
        loc_plural = rec[0, 1]
        
        A["count"].iloc[loc_nonplural] += A["count"].iloc[loc_plural]
        drop_ind = A.index[loc_plural]
        A = A.drop(axis="index", labels=drop_ind)
        
    if top10:
        A = A.nlargest(10, "count")
    
    return(A.sort_values(by="count", ascending=False))

def censor(A):
    bad_words = ["shit", "fuck", "nigga", "niggas"]
    censors = ["s***", "f***", "n****", "n****"]
    split = A.split(" ")
    for i in np.arange(len(split)):
        if split[i] in bad_words:
            for j in np.arange(len(bad_words)):
                if split[i] == bad_words[j]:
                    split[i] = censors[j]  
    x = " ".join(split)                           
    return(x)

# Top words by album
top15words = pd.read_csv("nl_data/top15words.csv")
top15words = top15words[["album", "count", "words"]]

## Other general adjustments:

# love lockdown and love-lockdown are separate
top15words.loc[top15words["words"] == "love lockdown", "count"] += top15words.loc[top15words["words"] == "love lock-down", "count"].to_numpy()[0]
drop_ind = top15words.index[top15words["words"] == "love lock-down"]
top15words = top15words.drop(axis="index", labels=drop_ind)
        
# Remove plurals
top10words = top15words.groupby("album").apply(remove_plurals)

# Censor curse words
censored_words = top10words["words"].apply(censor)
top10words["words"] = censored_words



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



# Create ordering based on album
album_sentiment = pd.read_csv("nl_data/album_sentiment.csv")
album_sentiment = album_sentiment[["album", "mean"]]
album_magnitude = pd.read_csv("nl_data/album_magnitude.csv")
album_magnitude = album_magnitude[["album", "mean"]]


album_order = ["The College Dropout", "Late Registration", "Graduation", "808s & Heartbreak", "My Beautiful Dark Twisted Fantasy", "Watch the Throne", "Yeezus", "The Life of Pablo", "ye", "Kids See Ghosts", "Jesus is King"]

top10words["album_key"] = pd.Categorical(top10words["album"], album_order)
top10sentences["album_key"] = pd.Categorical(top10sentences["album"], album_order)
bottom10sentences["album_key"] = pd.Categorical(bottom10sentences["album"], album_order)
album_sentiment["album_key"] = pd.Categorical(album_sentiment["album"], album_order)
album_magnitude["album_key"] = pd.Categorical(album_magnitude["album"], album_order)

raw = pd.read_csv("nl_data/raw_nl_data.csv")
raw["album_key"] = pd.Categorical(raw["album"], album_order)


# save all
raw.sort_values("album_key").to_csv("nl_data/raw_nl_data.csv")
top10sentences.sort_values("album_key").to_csv("nl_data/top10sentences.csv", index=False)
bottom10sentences.sort_values("album_key").to_csv("nl_data/bottom10sentences.csv", index=False)
top10words.sort_values("album_key").to_csv("nl_data/top10words.csv", index=False)
album_sentiment.sort_values("album_key").to_csv("nl_data/album_sentiment.csv", index=False)
album_magnitude.sort_values("album_key").to_csv("nl_data/album_magnitude.csv", index=False)
top10words_all.to_csv("nl_data/top10_overall.csv", index=False)