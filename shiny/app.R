library(shiny)
library(htmltools)
library(igraph)
library(networkD3)
library(dplyr)

# all available albums
albums <<- list("All", "The College Dropout", "Late Registration", 
           "Graduation", "808s & Heartbreak", 
           "My Beautiful Dark Twisted Fantasy", 
           "Watch the Throne", "Yeezus", 
           "The Life of Pablo", "ye", 
           "Kids See Ghosts", "Jesus is King")
create_nodes_links = function(album, min_connections){
  
  
  bigdf2 = read.csv("graph_data.csv")
  
  # Filter raw data by album
  albums = as.character(album)
  cat("album: ", album, "\n")
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



ui = fluidPage(
  titlePanel("Network of Entities"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("selection", "Select an Album:",
                  choices = albums),
      
      hr(),
      
      sliderInput("freq",
                  "Minimum Number of Occurences:",
                  min = 3, max = 8, value = 5
                  ),
      hr(),
      actionButton("update", "Update"),
    ),
    
    mainPanel(
      forceNetworkOutput("plot", height = "800px")
    )
  ),
)


server = function(input, output, session){
  
  # reactive expression for re-calculating nodes and links
  data = reactive({
    input$update
    isolate({
      withProgress({
        setProgress(message = "Loading network...")
        create_nodes_links(input$selection, input$freq)
      })
    })
  })
  
  
  output$plot = renderForceNetwork({
    dat = data()
    nodes = dat$nodes
    links = dat$links
    forceNetwork(links, nodes,
                      Source = "source", Target = "target",
                      NodeID = "name", Group = 1, Nodesize="size",
                      Value = "value", linkDistance = JS("function(d){return d.value * 10}"),
                      zoom=TRUE, opacity=0.9, opacityNoHover = 0.15,
                      linkColour = "#c2c2c2", charge = -150,
                      fontSize = 18, fontFamily = "Calibri")
  }
  )
  
}

shinyApp(ui = ui, server = server)
