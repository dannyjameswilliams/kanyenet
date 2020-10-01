library(shiny)
library(htmltools)
library(igraph)
library(networkD3)
library(dplyr)
library(shinythemes)
library(ggplot2)

# all available albums
albums <<- list("All", "The College Dropout", "Late Registration", 
           "Graduation", "808s & Heartbreak", 
           "My Beautiful Dark Twisted Fantasy", 
           "Watch the Throne", "Yeezus", 
           "The Life of Pablo", "ye", 
           "Kids See Ghosts", "Jesus is King")

albums_noall <<- list("The College Dropout", "Late Registration", 
                "Graduation", "808s & Heartbreak", 
                "My Beautiful Dark Twisted Fantasy", 
                "Watch the Throne", "Yeezus", 
                "The Life of Pablo", "ye", 
                "Kids See Ghosts", "Jesus is King")

album_colours = data.frame(
  albums = unlist(albums_noall),
  colours = c("#ab5918", "#311505", "#c74ac7", "#d1dad9", 
              "#ce1d34", "#a6894e", "#caccd5", "#f58c57", 
              "#1c2b48", "#e4554a", "#001da3"),
  stringsAsFactors = FALSE
)

album_colour_assign = c(
  "The College Dropout" = album_colours$colours[1],
  "Late Registration" = album_colours$colours[2],
  "Graduation" = album_colours$colours[3],
  "808s & Heartbreak" = album_colours$colours[4],
  "My Beautiful Dark Twisted Fantasy" = album_colours$colours[5],
  "Watch the Throne" = album_colours$colours[6],
  "Yeezus" = album_colours$colours[7],
  "The Life of Pablo" = album_colours$colours[8],
  "ye" = album_colours$colours[9],
  "Kids See Ghosts" = album_colours$colours[10],
  "Jesus is King" = album_colours$colours[11]
)

create_nodes_links = function(album, min_connections){
  
  
  bigdf2 = read.csv("data/graph_data.csv")
  
  # Filter raw data by album
  albums = as.character(album)
  if(albums != "All") bigdf2 = bigdf2[bigdf2$album %in% album,]
  
  # Method of reducing the dataset - only include words that occur more than 4 times
  bigdf2 = bigdf2[bigdf2$value >= min_connections,]
  
  bigdf2 = bigdf2[,c("name", "song", "value")]
  colnames(bigdf2)[2] = "variable"
  
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
  
  ## Get data in format for networkD3 forceNetwork plot
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
    
    # count
    links[i, 3] = as.numeric(bigdf4[i, "n"])
  }
  
  links = as.data.frame(links, stringsAsFactors = FALSE)
  colnames(links) = c("source", "target", "value")
  
  return(list(links=links, nodes=nodes))
}


get_density_plot = function(albums){
  sentiments = read.csv("data/sentiment_totals.csv")
  albums = unlist(albums)

  gg = ggplot() + xlab("Sentiment") + ylab("Density") + theme_minimal()
  
  album_dat = sentiments[sentiments$album %in% albums, ]
  colnames(album_dat)[2] = "Album"
  gg = gg + geom_histogram(data = album_dat, 
                           aes(sentiment, y= ..density.., 
                               fill=Album, col = Album), 
                               binwidth=0.1, alpha=0.6, position="identity") +
    geom_density(data = album_dat, aes(sentiment, col=Album), size=1.4)   

  gg = gg + scale_fill_manual(
    values = album_colour_assign
  ) + scale_colour_manual(
    values = album_colour_assign
  ) + theme(axis.text = element_text(size=15),
            axis.title = element_text(size=16),
            legend.title = element_text(size=16),
            legend.text = element_text(size=15))
  return(gg)
}

get_sentiment_by_song_plot = function(album, type){
  dat = read.csv("data/raw_nl_data.csv", stringsAsFactors = FALSE)
  colnames(dat)[c(6, 7)]= c("sentiment", "magnitude")
  dat = dat[,c("album", "song", type)]
  colnames(dat)[3] = "variable"
  
  song_order = read.csv("data/new_lyrics_clean.csv", stringsAsFactors = FALSE)
  song_order = song_order[,c("Album", "Song")]
  song_order$order = 1:nrow(song_order)
  colnames(song_order) = c("album", "song", "order")
  
  ylabel = type
  substr(ylabel, 1, 1) <- toupper(substr(ylabel, 1, 1))
  
  # filter to one album only
  dat = dat[dat$album == album, ]
  song_order = song_order[song_order$album == album, ]
  dat = dat %>% right_join(song_order, by = c("album", "song"))
  dat$song = factor(dat$song, levels = dat$song)
  colour = album_colours[album_colours$albums == album, "colours"]
  gg = ggplot(dat) + geom_bar(aes(x = song, y= variable), 
                              fill=colour, col = colour, 
                              alpha=0.8, stat = "identity") +
    xlab("Song") + ylab(ylabel) + theme_minimal() + 
    theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1),
          axis.text = element_text(size=15),  axis.title = element_text(size=16),)
  return(gg)
}

get_random_gpt2 = function(){
  text = readLines("data/generated_kanye_lyrics.txt")
  text = stringr::str_replace_all(text, "=", "")
  text = text[apply(as.matrix(text), 1, nchar) > 200]
  pick = sample(1:length(text), 1)
  
  split = stringr::str_split(text[pick], "\\. ")
  lines = split[[1]][nchar(split[[1]]) > 2]

  insertRow <- function(existingDF, newrow, r) {
    existingDF[seq(r+1,length(existingDF)+1)] <- existingDF[seq(r,length(existingDF))]
    existingDF[r] <- newrow
    existingDF
  }
  
  no_inserts = sample(2:round(length(lines)/4), 1)
  insert_places = seq(3, length(lines), length=no_inserts)
  for(i in insert_places) lines = insertRow(lines, " ", i)
  
  lines[1] = paste0('<p style="font-size:17px">', lines[1])
  lines[length(lines)] = "</p>"
  lines = paste0(lines, "<br/>")
  lines = apply(as.matrix(lines), 1, function(x) {
    x = stringr::str_replace_all(x, "\uFFFD", "'")
    return(x)
  })
  return(lines)
}

ui = fluidPage(

  tags$style("#controls {
                    background-color: rgba(213, 226, 247, 0.35);
                    font-size:16px;
                    width: 380px;
                    height:auto;
           }"),
  tags$style("#sent_controls {
                    background-color: rgba(213, 226, 247, 0.35);
                    font-size:16px;
                    height:auto;
           }"),
  tags$style("#sent_song_controls {
                    background-color: rgba(213, 226, 247, 0.35);
                    font-size:16px;
                    height:auto;
           }"),
  tags$style("#gpt2_controls {
                    background-color: rgba(213, 226, 247, 0.35);
                    height: auto
           }"),
  # Page with many tabs
  navbarPage(theme = shinytheme("paper"), collapsible = TRUE,
             "kanyenet",
             
    # Tab 1 for Entity Network
    tabPanel("Entity Network", id = "nav",
       div(class="outer", 
         tags$head(includeCSS("style.css")),
         
         tags$style(type = 'text/css', 
                    '.navbar { font-size: 18px;}',
                    'select {font-size: 15px}'
                    
         ),         
         mainPanel(id="graph",
                   forceNetworkOutput("network", height = "800px", width = "2400px")
         ),
       
         absolutePanel(id="controls", fixed = TRUE, class="card",
                       
              selectInput("selection", "Select an Album:",
                          choices = albums),
              
              hr(),
              
              sliderInput("freq",
                          "Minimum Number of Occurences",
                          min = 3, max = 8, value = 6
                          ),
              hr(),
              actionButton("networkinfo", "Info"),
              actionButton("update_network", "Update"),
              hr(),
              textOutput("networkinfo")
          )
       )
    ),
    # Tab 2 for Sentiment Analysis
    tabPanel("Sentiment Densities",
      tags$head(includeCSS("style.css")),   

      sidebarLayout(
      sidebarPanel(id = "sent_controls",
                   tags$style(type = 'text/css', 
                              'select {font-size: 25px}'
                              
                   ),  
                   checkboxGroupInput("album_checkboxes", "Select Albums:",
                             choices = albums_noall, selected = "The College Dropout"),
          hr(),
          actionButton("densityinfo", "Info"),
          hr(),
          textOutput("densityinfo")
      ),
      mainPanel(id = "densities",
          plotOutput("density", height = "600px")
        )
      )
             
    ),
    
    # Tab 3 for Sentiment by Song
    tabPanel("Sentiment by Song",
     tags$head(includeCSS("style.css"), tags$style(type = "text/css", "a{color: black;}")),        
     sidebarLayout(
       sidebarPanel(id = "sent_song_controls",
          tabsetPanel(id = "sentiment_magnitude",
              
              tabPanel("Sentiment", value = "sentiment", id="sent_tab",
                radioButtons("sentiment_checks", "Select Albums:",
                             choices = albums_noall, selected = "The College Dropout"),
                hr()      
              ),
              
              tabPanel("Magnitude", value = "magnitude", id="mag_tab",
                radioButtons("magnitude_checks", "Select Albums:",
                             choices = albums_noall, selected = "The College Dropout"),       
                hr()
              )
          ),
          actionButton("sentimentinfo", "Info"),
          hr(),
          textOutput("sentimentinfo")
       ),
       
       mainPanel(id = "song_barplot",
                 plotOutput("bars", height = "600px")
       )
     )
  ),
  
  # Tab 4 for GPT-2 generations
  tabPanel("GPT-2 Generations",
           tags$head(includeCSS("style.css"), tags$style(type = "text/css", "a{color: black;}")),        
           sidebarLayout(
             sidebarPanel(id = "gpt2_controls",
    
                          
               h4("Click below to see an AI generated Kanye West song."),
               h1("\n"),      
               h5("Content warning: this will not be censored at all, so offensive words may come up. In fact, they are quite likely to appear."),
               actionButton("gpt2info", "Info"),
               actionButton("generate_gpt2", "Give me Lyrics!"),
               hr(),      
               textOutput("gpt2info")     
             ),
             
             mainPanel(id = "gpt2",
                       htmlOutput("gpt2")
             )
           )
  )
)
)



server = function(input, output, session){
  
  # reactive expression for re-calculating nodes and links
  network_data = reactive({
    input$update_network
    isolate({
      withProgress({
        setProgress(message = "Loading network...")
        create_nodes_links(input$selection, input$freq)
      })
    })
  })
  
  # reactive for loading new density plots
  density_plot = reactive({
    withProgress({
      setProgress(message = "Loading plots...")
      get_density_plot(input$album_checkboxes)
    })
  })
  
  # reactive for song sentiment/magnitude plots
  song_sentiment_plot = reactive({
    withProgress({
      setProgress(message = "Loading plots...")
      if(input$sentiment_magnitude == "sentiment"){
        x = get_sentiment_by_song_plot(input$sentiment_checks, input$sentiment_magnitude)  
      } else if (input$sentiment_magnitude == "magnitude"){
        x = get_sentiment_by_song_plot(input$magnitude_checks, input$sentiment_magnitude)  
      }
    })
    x
  })
  
  
  # Plots for first three panels
  output$network = renderForceNetwork({
    dat = network_data()
    nodes = dat$nodes
    links = dat$links
    click_script = 'alert("Total count of \'" + (d.name) + "\': " + (d.size))'
    
    fn = forceNetwork(links, nodes,
                      Source = "source", Target = "target",
                      NodeID = "name", Group = 1, Nodesize="size",
                      Value = "value", linkDistance = JS("function(d){return d.value * 10}"),
                      zoom=TRUE, opacity=0.8, opacityNoHover = 0.25,
                      clickAction = click_script,
                      linkColour = "#c2c2c2", charge = -150,
                      fontSize = 22, fontFamily = "Calibri")
    
    fn$x$nodes$size <- nodes$size
    fn$x$nodes$name <- nodes$name
    fn
  })
  
  output$density = renderPlot({
    density_plot()
  })
  
  output$bars = renderPlot({
    song_sentiment_plot()
  })
  

  
  # Switches on and off info panel
  pressed = reactiveValues(
    network_pressed = FALSE,
    density_pressed = FALSE,
    sentiment_pressed = FALSE,
    gpt2_pressed = FALSE
  )
  
  # Info for network
  observeEvent(input$networkinfo,{
    pressed$network_pressed <<- !pressed$network_pressed
  })
  network_text = eventReactive(input$networkinfo, {
    text = "A network where the nodes represent distinct entities (important words), and the connections represent those entities being in the same song together. You can choose the album to view the network for, and change the minimum number of occurences of words - restricting it to only the most frequently occuring words across the album/all lyrics. <br/> Be careful when reducing the minimum number of occurences when using all the albums, it may slow down your machine."
    return(text)
  })
  
  # Info for density
  observeEvent(input$densityinfo,{
    pressed$density_pressed <<- !pressed$density_pressed
  })
  density_text = eventReactive(input$densityinfo, {
    "Densities of sentence sentiments for each album, so you can see how skewed in the positive/negative direction each album is. The sentiment is roughly how positive or negative a piece of text is."
  })
  
  # Info for sentiment
  observeEvent(input$sentimentinfo,{
    pressed$sentiment_pressed <<- !pressed$sentiment_pressed
  })
  sentiment_text = eventReactive(input$sentimentinfo, {
    "Plots of the sentiment/magnitude of each song. The sentiment is roughly how positive or negative a piece of text is. The magnitude is how emotional the song is; the sum of the absolute values of all sentence sentiments."
  })
  
  # Info for gpt2
  observeEvent(input$gpt2info,{
    pressed$gpt2_pressed <<- !pressed$gpt2_pressed
  })
  gpt2_text = eventReactive(input$gpt2info,{
    "These texts are pre-generated from OpenAI's GPT-2 language model, finetuned on all of Kanye's lyrics. The model was run for 10,000 steps with a learning rate of 1e-5. You may have to see a couple of generations before finding something good (the model can quite often get stuck)."
  })
  
  # Render generated song text for GPT-2
  gpt2_gen = eventReactive(input$generate_gpt2, {
    get_random_gpt2()
  })
  output$gpt2 = renderUI({
    HTML(gpt2_gen())
  })
  
  # Render info for different pages
  output$networkinfo = renderText({
    req(pressed$network_pressed == TRUE)
    invalidateLater(1000)
    network_text()
  })
  output$densityinfo = renderText({
    req(pressed$density_pressed == TRUE)
    invalidateLater(1000)
    density_text() 
  })
  output$sentimentinfo = renderText({
    req(pressed$sentiment_pressed == TRUE)
    invalidateLater(1000)
    sentiment_text()
  })
  output$gpt2info = renderText({
    req(pressed$gpt2_pressed == TRUE)
    invalidateLater(1000)
    gpt2_text()
  })
  
}

shinyApp(ui = ui, server = server)
