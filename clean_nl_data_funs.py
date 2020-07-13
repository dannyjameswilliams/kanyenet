import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")

import numpy as np
import pandas as pd
import operator
from functools import reduce
import ast

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
    
    A2 = A
    for j in np.arange(np.shape(rec)[0]):
        loc_nonplural = rec[j, 0]
        loc_plural = rec[j, 1]
        
        A2["count"].iloc[loc_nonplural] += A2["count"].iloc[loc_plural]
        
    for j in np.arange(np.shape(rec)[0]):
        loc_plural = rec[j, 1]
        drop_ind = A.index[loc_plural]
        A2 = A2.drop(axis="index", labels=drop_ind)
        
    if top10:
        A2 = A2.nlargest(10, "count")
    
    return(A2.sort_values(by="count", ascending=False))

def censor(A):
    bad_words = ["shit", "fuck", "nigga", "niggas", "motherfucker"]
    censors = ["s***", "f***", "n****", "n****", "motherf****er"]
    split = A.split(" ")
    for i in np.arange(len(split)):
        if split[i] in bad_words:
            for j in np.arange(len(bad_words)):
                if split[i] == bad_words[j]:
                    split[i] = censors[j]  
    x = " ".join(split)                           
    return(x)

def getallwords(A):
    
    drop_ind1 = A.index[A["words"] == "one"]
    drop_ind2 = A.index[A["words"] == "thing"]
    A = A.drop(axis=0, labels=drop_ind1)
    A = A.drop(axis=0, labels=drop_ind2)
    
    B = np.empty(A.shape[0], dtype="<U1000")
    
    for i in np.arange(B.shape[0]):
        c = np.repeat(A.iloc[i]["words"], A.iloc[i]["count"])
        B[i] = " ".join(c)
    x = " ".join(B)
    x2 = x.split(" ")
    np.random.shuffle(x2)
    return(" ".join(x2))


def mean_sd(A, name):
    m = np.mean(A[name])
    s = np.std(A[name])
    out = pd.DataFrame(index = [0], columns = ["mean", "sd"])
    out["mean"] = m
    out["sd"] = s
    return(out)

def sort_by_album(A):
    from variables import album_order
    inds = A.columns
    if "album" not in A.columns: 
        alb_bool = ["album" == i for i in A.index.names]
        A["album"] = A.index.levels[np.where(alb_bool)[0][0]]
    
    A["album_key"] = pd.Categorical(A["album"], album_order)
    A = A.sort_values(by="album_key")
    return(A[inds])


def sentence_sentiment(A):
    n = len(A.sentences)
    df = pd.DataFrame(index=np.arange(0), columns=["sentiment"])
    for i in np.arange(n):
        s  = A.sentences.iloc[i]
        s2 = ast.literal_eval(s[1:(len(s)-1)])
        d = pd.DataFrame.from_records(s2, index=["sentiment"]).T
        df = df.append(d)
    df["album"] = A.album.iloc[0]
    return(df)
    
def add_noise(A):
    A["noise"] = np.random.uniform(size=len(A))
    return(A)
    