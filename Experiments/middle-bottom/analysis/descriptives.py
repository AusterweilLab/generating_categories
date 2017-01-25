import sqlite3, sys
import pandas as pd
import numpy as np

sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

pd.set_option('display.width', 120, 'precision', 2)

con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
counterbalance = pd.read_sql_query("SELECT * from counterbalance", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

print participants.shape

# counts per condition
print(participants.groupby('condition').size())
print 

participants = pd.merge(participants, counterbalance, on = 'counterbalance')
print pd.pivot_table(
	data = participants,
	columns = 'xax',
	index = 'condition',
	aggfunc = 'size'
	)



stats = pd.merge(stats, participants, on = 'participant')
from scipy.stats import ttest_ind, mannwhitneyu
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
	print S
