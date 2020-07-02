# Natural Language Processing of Kanye West's Lyrics

Experimentation with Google APIs such as the [Natural Language API](https://cloud.google.com/natural-language), and data visualisation.

This project aims to provide some interesting analysis of the lyrics in the discography of Kanye West. This is restricted to his studio albums, but not solo albums, so that his collaborations with Kid Cudi and Jay Z are included.
These albums are *The College Dropout*, *Late Registration*, *Graduation*, *808's and Heartbreaks*, *My Beautiful Dark Twisted Fantasy*, *Watch the Throne*, *Yeezus*, 
*The Life of Pablo*, *ye*, *Kids See Ghosts* and *Jesus is King*. 

Mostly written in Python 3, but the [genius](https://cran.r-project.org/web/packages/genius/index.html) package in R was used to scrape lyrics for each song. 
Although this method returned empty strings for a significant number of songs, so in some places, manual copying and pasting from [Genius](https://genius.com/artists/Kanye-west) was required.
