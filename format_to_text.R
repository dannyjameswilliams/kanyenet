lyrics = read.csv("data/new_lyrics_clean.csv")
lyrics = as.character(lyrics$Lyrics)


lyrics_out = rep(NA, length(lyrics))
for(i in 1:length(lyrics)){
  split1 = strsplit(lyrics[i], "\\.")
  rem = apply(as.matrix(split1[[1]]),1, nchar) <= 1
  split1 = split1[[1]][!rem]
  split2 = paste(split1, collapse=".") 
  lyrics_out[i] = split2
}


writeLines(lyrics_out, "data/kanye_lyrics.txt")
