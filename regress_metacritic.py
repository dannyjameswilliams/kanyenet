import os
os.chdir("/home/fs19144/Documents/Summer_Projects/kanyenet")


import regress_metacritic_funs as rmf

fit_mag, fit_sen = rmf.fit_model()

#rmf.plot_matplotlib(fit_mag,fit_sen)
rmf.plot_plotly(fit_mag, fit_sen, True)
