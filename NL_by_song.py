import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")

import numpy as np
import pandas as pd
import operator
from functools import reduce

def applyf(A, type="words", nlargest=0, nsmallest=0):
    all_words = [x[0] for x in A[type]]
    
    def combine_dicts(a, b, op=operator.add):
        return {**a, **b, **{k: op(a[k], b[k]) for k in a.keys() & b}}
    
    word_totals = pd.DataFrame.from_records(reduce(combine_dicts, all_words), index=["count"])
    colnames = word_totals.columns
    word_totals = word_totals.T
    word_totals["words"] = colnames
    word_totals = word_totals.sort_values(by="count", ascending=False)
    if nlargest > 0:
        word_totals = word_totals.nlargest(nlargest, "count")
    elif nsmallest > 0:
        word_totals = word_totals.nsmallest(nsmallest, "count")
        
    return(word_totals)
    
if __name__ == "__main__":
    # Read Data
    filename = "data/new_lyrics_clean.csv"
    df = pd.read_csv(filename)

    # Remove some NA (all of the lights interlude - no lyrics)
    nas = df["Lyrics"].isna() 
    df = df[~nas]
    #df = df.iloc[[1, 90, 40]]

    # Import google cloud library for NL processing
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/fs19144/Documents/Other/api_keys/gcp_nl.json"
    from google.cloud import language
    from google.cloud.language import enums, types

    # Pre define data frame for saving NL attributes
    n = df.shape[0]
    col_names = ["album", "song", "words", "types", "song_sentiment", "song_magnitude", "sentences"]
    word_data = pd.DataFrame(index=np.arange(n), columns=col_names)

    # Set album and song
    word_data["album"] = df.Album.to_numpy()
    word_data["song"] = df.Song.to_numpy()

    # Load the google NL client
    client = language.LanguageServiceClient()

    # Loop over each song, perform NL at each step
    # DO NOT RUN WITHOUT THINKING -- Charges could be below
    for i in np.arange(n):

        # Get text and convert for analysis
        song_lyrics = df["Lyrics"].iloc[i].lower()
        document = types.Document(
            content=song_lyrics,
            type=enums.Document.Type.PLAIN_TEXT
        )

        ## -- Sentiment score
        all_sentiments = client.analyze_sentiment(document)

        # Create dictionary of all different sentences with corresponding sentiment score
        # Since each sentence will be unique, there should  be no overlap
        n_sent = len(all_sentiments.sentences)
        diff_sentences = {}
        for j in np.arange(n_sent):
            sentence = all_sentiments.sentences[j]
            diff_sentences[sentence.text.content] = sentence.sentiment.score

        # Fall back - if the API does not output a sentiment score, use the mean of all sentences
        if all_sentiments.document_sentiment.score == 0.0:
            main_sentiment = pd.DataFrame.from_records(diff_sentences, index=[0]).T.mean()[0]
        else:
            main_sentiment = all_sentiments.document_sentiment.score

        word_data.song_sentiment.iloc[i] = main_sentiment
        word_data.song_magnitude.iloc[i] = all_sentiments.document_sentiment.magnitude
        word_data.sentences.iloc[i] = [diff_sentences]

        ## -- Counts of entities
        all_entities = client.analyze_entities(document)

        # Create dictionary of different words per song, sum the occurences of each word entity
        n_ents = len(all_entities.entities)
        diff_words = {}; diff_types = {}
        for j in np.arange(n_ents):
            ent = all_entities.entities[j]
            t = str(enums.Entity.Type(ent.type)).lower()
            t = t[5:len(t)]
            num = len(all_entities.entities[j].mentions)
            if ent.name in diff_words:
                diff_words[ent.name] = diff_words[ent.name] + num
            else:
                diff_words[ent.name] = num

            if t in diff_types:
                diff_types[t] = diff_types[t] + num
            else:
                diff_types[t] = num

        word_data.words.iloc[i] = [diff_words]
        word_data.types.iloc[i] = [diff_types]



    # Top 15 words for each album
    top15words = word_data.groupby("album").apply(lambda x: applyf(x, nlargest=15))

    # Top 15 types for each album
    top15types = word_data.groupby("album").apply(lambda x: applyf(x, type="types", nlargest=15))


    # Highest/lowest scoring sentences for each album
    top15sentences = word_data.groupby("album").apply(lambda x: applyf(x, type="sentences", nlargest=15))
    bottom15sentences = word_data.groupby("album").apply(lambda x: applyf(x, type="sentences", nsmallest=15))

    # Mean sentiment for each album
    word_sentiment = word_data[["album", "song_sentiment"]]
    word_sentiment["song_sentiment2"] = word_sentiment["song_sentiment"]
    album_sentiment = word_sentiment.groupby("album").agg({'song_sentiment':'sum','song_sentiment2':'count'})
    album_sentiment["mean"] = album_sentiment["song_sentiment"]/album_sentiment["song_sentiment2"]
    album_sentiment = album_sentiment[["mean"]]

    # Mean magnitude for each album
    word_magnitude = word_data[["album", "song_magnitude"]]
    word_magnitude["song_magnitude2"] = word_magnitude["song_magnitude"]
    album_magnitude = word_magnitude.groupby("album").agg({'song_magnitude':'sum','song_magnitude2':'count'})
    album_magnitude["mean"] = album_magnitude["song_magnitude"]/album_magnitude["song_magnitude2"]
    album_magnitude = album_magnitude[["mean"]]

    # Save outputs
    top15sentences.to_csv("nl_data/top15sentences.csv", index=True)
    bottom15sentences.to_csv("nl_data/bottom15sentences.csv", index=True)
    top15types.to_csv("nl_data/top15types.csv", index=True)
    top15words.to_csv("nl_data/top15words.csv", index=True)
    album_sentiment.to_csv("nl_data/album_sentiment.csv", index=True)
    album_magnitude.to_csv("nl_data/album_magnitude.csv", index=True)
    word_data.to_csv("nl_data/raw_nl_data.csv", index=False) 
    word_data.to_pickle("nl_data/raw_nl_data", index=False)