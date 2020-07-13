# Natural Language Processing of Kanye West's Lyrics

## Overview

Read the blog post describing the analysis [on my personal website](http://dannyjameswilliams.co.uk/post/kanye).

Experimentation with Google APIs such as the [Natural Language API](https://cloud.google.com/natural-language), and data visualisation.

This project aims to provide some interesting analysis of the lyrics in the discography of Kanye West. This is restricted to his studio albums, but not solo albums, so that his collaborations with Kid Cudi and Jay Z are included.
These albums are *The College Dropout*, *Late Registration*, *Graduation*, *808's and Heartbreaks*, *My Beautiful Dark Twisted Fantasy*, *Watch the Throne*, *Yeezus*, 
*The Life of Pablo*, *ye*, *Kids See Ghosts* and *Jesus is King*. 

### Data
The [genius](https://cran.r-project.org/web/packages/genius/index.html) package in R was used to scrape lyrics for each song. 
Although this method returned empty strings for a significant number of songs, so in some places, manual copying and pasting from [Genius](https://genius.com/artists/Kanye-west) was required.

## Code Structure

Mostly written in Python 3, but some parts are written in R.
For the majority of the Python code, each file has two parts, the part to be run and the part containing the function definitions. Below is a list of files and what they are used for:

- **clean_data.py**: *Unneeded for reproducing results*, was originally used to process the raw data.
- **NL_by_song.py**: *Unneeded for reproducing results*, and also it won't work without an API key. This is where Google's natural language API is called. Each song is passed individually in a loop. The count of each entity and entity type are saved in a dictionary, contained in a `pandas` `DataFrame`. The sentiment and magnitude of each song (and each sentence) are also saved here.
- **clean_nl_data.py**: *Unneeded for reproducing results*, used for processing the data after it has been passed through the API. Here the top 10 words are processed, sentiments are grouped by albums etc. This is the data read in when producing visualisations.
- **visualise.py**: Used for creating all plots in the blog post.
- **regress_metacritic.py**: Used for creating the regression plots of metacritic score against sentiment/magnitude. Can either plot interactively via `plotly` or with `matplotlib`. The `plotly` plots will not be able to be saved to your `plotly` account unless you supply an API and username.

