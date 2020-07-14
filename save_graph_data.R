library(stringr)
library(tidyverse)

## Read and load data
raw       = read.csv("nl_data/raw_nl_data.csv", stringsAsFactors = FALSE)
all_words = as.character(raw$words)
albums    = as.character(unique(raw$album))
bigdf     = matrix(0, 0, length(all_words)+1)
colnames(bigdf) = c("name", as.character(raw$song))

## Loop over word dictionaries, do string editing to convert to R dataframe
# Concatenate data frame into a larger dataframe
for(i in 1:length(all_words)){
  lyrics = all_words[i]
  lyrics = substr(lyrics, 2, nchar(lyrics)-1)
  
  song_name = as.character(raw$song[i])
  song_pos = which(raw$song %in% song_name) + 1
  
  words = stringr::str_split(lyrics, ",")
  
  # Catch errors in splitting, manually subset
  bad_split = which(!(substr(words[[1]][2:length(words[[1]])],1,2) == " '" |
                        substr(words[[1]][2:length(words[[1]])],1,2) ==' \"')) + 1
  
  joined = paste0(words[[1]][bad_split-1], words[[1]][bad_split])
  words[[1]][bad_split-1] = joined
  words[[1]][bad_split] = NA
  words[[1]] = words[[1]][!is.na(words[[1]])]
  
  # Create smaller dataframe to append to larger one
  df = as.data.frame(matrix(0, length(words[[1]]), length(all_words)+1), stringsAsFactors=FALSE)
  colnames(df) = c("name", as.character(raw$song))
  for(j in 1:length(words[[1]])){
    line = words[[1]][j]
    split = strsplit(line, ":")
    
    name = split[[1]][1]
    name = substr(name, 3, nchar(name)-1)
    
    value = split[[1]][2]
    if(substr(value, nchar(value), nchar(value)) == "}"){
      value = substr(value, 1, nchar(value)-1)
    }
    if(is.na(as.numeric(value))) cat("i = ", i, "name = ", name, ", value = ", value, "j = ", j, "\n")
    value = as.numeric(value)
    
    df[j, 1] = name
    df[j, song_pos] = value
    
  }
  bigdf = rbind(bigdf, df)
}

## Convert sparse matrix into long format dataframe
library(reshape2)
bigdf2 = melt(bigdf)

bigdf2 = bigdf2[bigdf2$value!=0,]
bigdf2 = bigdf2[sample(1:nrow(bigdf2), nrow(bigdf2)),]
bigdf2 = bigdf2[order(bigdf2$value, decreasing = TRUE),]


# Remove plurals from words
remove_plurals = function(x){
  ignores = c("jesus", "baby jesus", "glass", "mars", 
              "ass","parties", "glasses", "stress", "bitches")
  if(x %in% ignores) return(x)
  if(substr(x, nchar(x), nchar(x)) == "s"){
    x = substr(x, 1, nchar(x)-1)
  }
  if(substr(x, nchar(x)-1, nchar(x)) == "es"){
    x = substr(x, 1, nchar(x)-2)
  }
  return(x)
}
no_plurals = apply(as.matrix(bigdf2$name), 1, remove_plurals)
bigdf2$name = no_plurals

# love lockdown

# Censor bad words [content warning]
badwords = c("fuck", "shit", "nigga")
replacements = c("f***", "s***", "n****")
censor = function(x){
  loc_censor = stringr::str_detect(x, badwords)
  if(any(loc_censor)) {
    if(sum(loc_censor) > 1){
      y = x
      for(j in 1:sum(loc_censor)){
        y = stringr::str_replace(y, badwords[which(loc_censor)[j]], 
                                 replacements[which(loc_censor)[j]])
      }
    } else{
      y = stringr::str_replace_all(x, badwords[loc_censor],
                                   replacements[loc_censor])
    }
    return(y)
  } else{
    return(x)
  }
}
censored_words = apply(as.matrix(bigdf2$name), 1, censor)
bigdf2$name = unlist(censored_words)

# Remove same word to same word mappings and small words (probable errors) 
bigdf2 = bigdf2[!apply(bigdf2, 1, function(x) x[1] == x[2]),]
bigdf2 = bigdf2[apply(bigdf2, 1, function(x) nchar(x[1]) > 2 & nchar(x[2]) > 2),]

album_map = raw[,c("album", "song")]
colnames(bigdf2) = c("name", "song", "value")
graph_data = bigdf2 %>% right_join(album_map, by="song")
write.csv(graph_data, "nl_data/graph_data.csv")
