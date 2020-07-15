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

create_nodes_links = function(album, min_connections){
  
  
  bigdf2 = read.csv("graph_data.csv")
  
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

ui = fluidPage(
      titlePanel("Network of Entities in the Lyrics of Kanye West"),
      
       tags$head(includeCSS("style.css")),
    
       mainPanel(id="graph",
                 forceNetworkOutput("network", height = "800px", width = "2400px")
       ),
     
       absolutePanel(id="controls", fixed = TRUE, class="card",
                     
            selectInput("selection", "Select an Album:",
                        choices = albums),
            
            hr(),
            
            sliderInput("freq",
                        "Minimum Number of Occurences:",
                        min = 3, max = 8, value = 5
                        ),
            hr(),
            actionButton("update_network", "Update"),
        )
)



server = function(input, output, session){
  
  network_data = reactive({
    input$update_network
    isolate({
      withProgress({
        setProgress(message = "Loading network...")
        create_nodes_links(input$selection, input$freq)
      })
    })
  })
  
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

  
}

shinyApp(ui = ui, server = server)
