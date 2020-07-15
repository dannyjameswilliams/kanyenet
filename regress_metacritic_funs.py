import numpy as np
import pandas as pd
import sklearn.linear_model as lm
import matplotlib.pyplot as plt
from variables import *

import plotly_keys as mykeys
import chart_studio
chart_studio.tools.set_credentials_file(username=mykeys.username,
                                        api_key=mykeys.api)

import chart_studio.plotly as py
import plotly.graph_objs as go
import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")


def fit_model():
    metacritic = pd.read_csv("data/metacritic.csv")
    metacritic.index = metacritic["album"]
    fit_mag =  lm.LinearRegression(fit_intercept=True).fit(metacritic[["magnitude_mean"]],
                    metacritic["score"])
    fit_sen =  lm.LinearRegression(fit_intercept=True).fit(metacritic[["sentiment_mean"]],
                    metacritic["score"])
    print("Magnitude Model:: Intercept: {}, Gradient: {}, R^2:  {}".format(fit_mag.intercept_, fit_mag.coef_, fit_mag.score(metacritic[["magnitude_mean"]], metacritic["score"])))
    print("Sentiment Model:: Intercept: {}, Gradient: {}, R^2: {}".format(fit_sen.intercept_, fit_sen.coef_, fit_sen.score(metacritic[["sentiment_mean"]], metacritic["score"])))

    
    return fit_mag, fit_sen


def plot_matplotlib(fit_mag, fit_sen):
    metacritic = pd.read_csv("data/metacritic.csv")
    metacritic.index = metacritic["album"]
    fig, axs = plt.subplots(1, 2)
    
    axs[0].scatter(metacritic["magnitude_mean"], metacritic["score"], c=colours)
    axs[0].plot(metacritic["magnitude_mean"], [fit_mag.intercept_ + fit_mag.coef_[0]*i for i in metacritic["magnitude_mean"].to_numpy()], 'r')#
    
    axs[1].scatter(metacritic["sentiment_mean"], metacritic["score"], c=colours)
    axs[1].plot(metacritic["sentiment_mean"], [fit_sen.intercept_ + fit_sen.coef_*i for i in metacritic["sentiment_mean"].to_numpy()], 'r')
    plt.show()
    
def plot_plotly(fit_mag, fit_sen, save=False):
    metacritic = pd.read_csv("data/metacritic.csv")
    metacritic.index = metacritic["album"]
    # regression lines
    line_sen = [fit_sen.intercept_ + fit_sen.coef_[0]*i for i in metacritic["sentiment_mean"].to_numpy()]
    line_mag = [fit_mag.intercept_ + fit_mag.coef_[0]*i for i in metacritic["magnitude_mean"].to_numpy()]

    # Sentiment
    i = 0
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=metacritic["sentiment_mean"], 
                             y=metacritic["score"],
                             mode='markers',
                             name='markers',
                             marker=dict(
                                      size=16,
                                      color=colours
                                     ),
                             hovertext=metacritic['album'],
                             hoverlabel=dict(namelength=0),
                            hovertemplate='<b>%{hovertext}</b><br>Sentiment: %{x} <br>Score: %{y}'
        )
    )
    fig1.add_trace(go.Scatter(x=metacritic["sentiment_mean"], 
                             y=line_sen,
                             mode='lines',
                             name='lines',
                             hovertext="Regression Line",
                             hoverlabel=dict(namelength=0)))

    fig1.update_layout(
        xaxis_title = "Album Mean Sentiment",
        yaxis_title = "Album Metacritic Score",
        template = "plotly_white",
        showlegend=False
    )
    fig1.show()
    if save: py.plot(fig1, filename = "sentiment", auto_open=True)
    
    # Magnitude
    i = 2
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=metacritic["magnitude_mean"], 
                             y=metacritic["score"],
                             mode='markers',
                             name='markers', 
                             marker=dict(
                                      size=16,
                                      color=colours
                                     ),
                             hovertext=metacritic['album'],
                             hoverlabel=dict(namelength=0),
                             hovertemplate='<b>%{hovertext}</b><br>Magnitude: %{x} <br>Score: %{y}'
        )
    )
    fig2.add_trace(go.Scatter(x=metacritic["magnitude_mean"], 
                             y=line_mag,
                             mode='lines',
                             name='lines',
                             hovertext="Regression Line",
                             hoverlabel=dict(namelength=0)))

    fig2.update_layout(
        xaxis_title = "Album Mean Magnitude",
        yaxis_title = "Album Metacritic Score",
        template = "plotly_white",
        showlegend=False
    )
    fig2.show()
    if save: py.plot(fig2, filename = "magnitude", auto_open=True)