import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")
import numpy as np
import pandas as pd
import sklearn.linear_model as lm
import matplotlib.pyplot as plt

metacritic = pd.read_csv("data/metacritic.csv")
metacritic.index = metacritic["album"]
model = lm.LinearRegression(fit_intercept=True)
fit = model.fit(metacritic[["magnitude_mean", "sentiment_mean"]],
                metacritic["score"])

print("Intercept: {}, Gradient: {}".format(fit.intercept_, fit.coef_))


plt.scatter(metacritic["magnitude_mean"], metacritic["score"])
plt.plot(metacritic["magnitude_mean"], [fit.intercept_ + fit.coef_[0]*i for i in metacritic["magnitude_mean"].to_numpy()])
scatter_matrix(metacritic[["score","magnitude_mean", "sentiment_mean"]], figsize=(16, 16));
plt.show()
