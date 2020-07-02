library(genius)
setwd("~/Documents/Summer_Projects/kanyenet/data")

# Start with a data frame of just song titles and album names
lyrics = read.csv("song_album.csv")
lyrics$Song = as.character(lyrics$Song)
lyrics$Lyrics = NA

# Loop over and call genius library to get lyrics
start = 1
end = nrow(lyrics)
for(i in start:end){
  artist = "kanye west"
  if(i >= 129 & i <= 135) artist = "KIDS SEE GHOSTS"
  lines = genius_lyrics(artist, song=as.character(lyrics[i,"Song"]))
  x = paste(lines$lyric, sep="\n", collapse="\n")
  lyrics[i,"Lyrics"] = as.character(x)
}

# Sometimes the genius function fails
# View which songs need to be manually entered
empties = apply(as.matrix(lyrics$Lyrics), 1, nchar) == 0
lyrics$Song[empties]

# Write to CSV for compatability with python
write.csv(lyrics, "new_lyrics.csv")
