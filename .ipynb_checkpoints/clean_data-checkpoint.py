import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")

import numpy as np
import pandas as pd
import re

# Read hand coded data
df = pd.read_csv("data/new_lyrics.csv")
n = df.shape[0]
for i in np.arange(n):
    x = df["Lyrics"].iloc[i]
    x = re.sub("[\(\[].*?[\)\]]", "", x)
    df["Lyrics"].iloc[i] = x
    
# remove /n from beginning of words
startswithn = df["Lyrics"].str.startswith("\n")
df_withn = df[startswithn]
for i in np.arange(sum(startswithn)):
    x = df_withn.Lyrics.iloc[i]
    nr = len(x)
    df_withn.Lyrics.iloc[i] = x[1:nr] 
df[startswithn] = df_withn
df.Lyrics = df.Lyrics.str.replace("\n", ". ")

# remove skits
not_skit = df["Skit"] == "N"
df = df[not_skit]

# save to a new cleaner data csv
df.to_csv("data/new_lyrics_clean.csv")
