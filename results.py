import pylab as pl
import pandas as pd

df = pd.read_csv('resultados.txt')
dff = df.groupby('ia')
scores = dff['score']
times = dff['time']
maxs = dff['max']
pl.ylabel('Scores (points)')
scores.mean().plot.bar(x='ia')
pl.show()
pl.ylabel('Time (s)')
times.mean().plot.bar(x='ia')
pl.show()
pl.ylabel('Minimum max tile')
maxs.min().plot.bar(x='ia')
pl.show()
pl.ylabel('Maximum max tile')
maxs.max().plot.bar(x='ia')
pl.show()
