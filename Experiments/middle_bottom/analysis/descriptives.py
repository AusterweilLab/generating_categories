import sqlite3, sys,os
import pandas as pd
import numpy as np

pd.set_option('display.width', 120, 'display.precision', 2)

os.chdir(sys.path[0])


con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
counterbalance = pd.read_sql_query("SELECT * from counterbalance", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

print(participants.shape)

# counts per condition
print(participants.groupby('condition').size())
print()

participants = pd.merge(participants, counterbalance, on = 'counterbalance')
print(pd.pivot_table(
	data = participants,
	columns = 'xax',
	index = 'condition',
	aggfunc = 'size'
	))



stats = pd.merge(stats, participants, on = 'participant')
from scipy.stats import ttest_ind, mannwhitneyu, ttest_rel
cols = ['area','between','within',
				'correlation', 
				'drange', 'xrange', 'yrange', 'xstd', 'ystd']

for i in cols:
	gs = list(stats.groupby('condition')[i])
	d = dict(gs)
	ms = dict([(k, np.mean(v)) for k,v in d.items()])
	p = mannwhitneyu(d['Middle'], d['Bottom']).pvalue

	S = i
	for k,v in d.items():
		S += '\t' + k + ' = ' + str(round(np.mean(v),3))
	S += '\t' + 'p = ' + str(round(p,3))
	print(S)


for j, rows in stats.groupby('condition'):
	g1 = rows['within'].to_numpy()
	g2 = rows['between'].to_numpy()
	print(j, ttest_rel(g1, g2))

