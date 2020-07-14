library(shiny)
library(networkD3)

ui = fluidPage( 
  
  titlePanel("ForceNetD3"), 
  
  sidebarLayout(
    sidebarPanel(
      sliderInput("opacity",
                  "Opacity",
                  min = 0.1,
                  max = 1,
                  value = 0.4)
    ),
    mainPanel(
      forceNetworkOutput(outputId = "net")
    )
))

server = function(input, output) {
  
  # Load data
  data(MisLinks)
  data(MisNodes)      
  
  output$net <- renderForceNetwork(forceNetwork(
    Links  = MisLinks, Nodes   = MisNodes,
    Source = "source", Target  = "target",
    Value  = "value",  NodeID  = "name",
    Group  = "group",  opacity = input$opacity))
}

shinyApp(ui = ui, server = server)
