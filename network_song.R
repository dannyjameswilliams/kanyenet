## Read and load data
raw       = read.csv("nl_data/raw_nl_data.csv")
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
#bigdf2 = bigdf2[1:100,]

# Remove plurals from words
remove_plurals = function(x){
  if(substr(x, nchar(x), nchar(x)) == "s"){
    x = substr(x, 1, nchar(x)-1)
  }
  return(x)
}
no_plurals = apply(as.matrix(bigdf2$name), 1, remove_plurals)
bigdf2$name = no_plurals

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

# Remove same word to same word mappings, small words (probable errors) and single use words
bigdf2 = bigdf2[!apply(bigdf2, 1, function(x) x[1] == x[2]),]
bigdf2 = bigdf2[apply(bigdf2, 1, function(x) nchar(x[1]) > 2 & nchar(x[2]) > 2),]
bigdf2 = bigdf2[bigdf2$value > 3,]


## Two column dataframe mappings from word to word
songs = as.character(unique(bigdf2$variable))
bigdf3 = matrix(NA, 0, 2); colnames(bigdf3) = c("from", "to")
for(i in 1:length(songs)){
  
  pos = which(bigdf2$variable %in% songs[i])
  indf = bigdf2[pos,]
  smalldf = matrix(NA, 0, 2)
  for(j in 1:length(pos)){
    indf2 = matrix(NA, nrow(indf), 2)
    indf2[ ,1] = as.character(indf[j,1])
    indf2[ ,2] = as.character(indf[ ,1])
    smalldf = rbind(smalldf, indf2)
  }
  bigdf3 = rbind(bigdf3, smalldf)
}


# Libraries
library(igraph)
library(networkD3)

# Count number of unique pairs of mappings
bigdf3 = as.data.frame(bigdf3, stringsAsFactors=FALSE)
bigdf4 = data.frame(t(apply(bigdf3,1,sort)), stringsAsFactors = FALSE) %>% group_by_all %>% count()

colnames(bigdf4) = c("from", "to", "n")



# Get data in format for networkD3 forceNetwork plot

nodes = data.frame(name = unlist(bigdf2$name), 
                   group = as.numeric(as.factor(bigdf2$variable)),
                   size = bigdf2$value, stringsAsFactors=FALSE)
nodes = nodes %>% group_by(name) %>%  summarise(size = sum(size))
nodes_i = 1:nrow(nodes) - 1
links = matrix(NA, nrow(bigdf4), 3)
for(i in 1:nrow(bigdf4)){
  # from 
  from = as.character(bigdf4[i, "from"])
  from_w = which(nodes$name %in% from)
  links[i, 1] = nodes_i[from_w] 
  
  # to
  to = as.character(bigdf4[i, "to"])
  to_w = which(nodes$name %in% to)
  links[i, 2] = nodes_i[to_w] 
  
  links[i, 3] = as.numeric(bigdf4[i, "n"])
}

links = as.data.frame(links, stringsAsFactors = FALSE)
colnames(links) = c("source", "target", "value")


write.csv(links, "nl_data/graph_links.csv")
write.csv(nodes, "nl_data/graph_nodes.csv")


# library(htmltools)
# browsable(
#   tagList(
#     tags$head(
#       tags$style('
#         .nodetext{fill: #000000}
#         .legend text{fill: #FF0000}
#       ')
#     ),
#     forceNetwork(links, as.data.frame(nodes),
#              Source = "source", Target = "target",
#              NodeID = "name", Group = 1, Nodesize="size", 
#              Value = "value",
#              zoom=TRUE, opacity=0.9,
#              fontSize = 14)
# ))
