import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

execfile('Imports.py')
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')


fh, axes = plt.subplots(1,3,figsize = (9,3))
for i, col in enumerate(['xrange','yrange','correlation']):
	ax = axes[i]
	sns.factorplot(x = 'condition', y = col, data= stats, ax = ax, kind = 'box', 
		order = ['Cluster', 'Row','XOR'])

	ax.set_title(col, fontsize = 14)
	ax.set_ylabel('')

	if 'range' in col:
		ax.set_title(col[0].upper() + ' Range', fontsize = 14)
	else:
		ax.set_title('Correlation', fontsize = 14)

	ax.tick_params(labelsize = 12)
	ax.set_xlabel('')
	ax.xaxis.grid(False)

fh.subplots_adjust(wspace=0.4)
fh.savefig('statsboxes.pdf', bbox_inches = 'tight', pad_inches=0.0)


# hypothesis tests
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp
from itertools import combinations

def print_ttest(g1, g2, fun):
	res = fun(g1,g2)
	S = 'T = ' + str(round(res.statistic, 4))
	S+= ', p = ' + str(round(res.pvalue, 10))
	S+= '\tMeans:'
	for j in [g1, g2]:
		S += ' ' + str(round(np.mean(j), 4))
		S +=  ' (' + str(round(np.std(j), 4)) + '),'
	print S


print '\n---- Row X vs. Y:'
g1 = stats.loc[stats.condition == 'Row', 'xrange']
g2 = stats.loc[stats.condition == 'Row', 'yrange']
print_ttest(g1,g2, ttest_rel)

print '\n---- Cluster X vs. Y:'
g1 = stats.loc[stats.condition == 'Cluster', 'xrange']
g2 = stats.loc[stats.condition == 'Cluster', 'yrange']
print_ttest(g1,g2, ttest_rel)

print '\n---- XOR X vs. Y:'
g1 = stats.loc[stats.condition == 'XOR', 'xrange']
g2 = stats.loc[stats.condition == 'XOR', 'yrange']
print_ttest(g1,g2, ttest_rel)

print '\n---- XOR negative correlation?'
g1 = stats.loc[stats.condition == 'XOR', 'correlation']
print ttest_1samp(g1, 0).pvalue

print '\n---- XOR has more total range than Cluster?'
g1 = stats.loc[stats.condition == 'Cluster', ['xrange','yrange']].sum(axis = 1)
g2 = stats.loc[stats.condition == 'XOR', ['xrange','yrange']].sum(axis = 1)
print_ttest(g1,g2, ttest_ind)

print '\n---- XOR has more total range than Row?'
g1 = stats.loc[stats.condition == 'Row', ['xrange','yrange']].sum(axis = 1)
g2 = stats.loc[stats.condition == 'XOR', ['xrange','yrange']].sum(axis = 1)
print_ttest(g1,g2, ttest_ind)


# between conditions
for j in ['xrange','yrange','correlation']:
	for a, b in combinations(pd.unique(stats.condition), r=2):
		g1 = stats.loc[stats.condition == a, j]
		g2 = stats.loc[stats.condition == b, j]
		print '\n---- ' + ' ' + j + ': ' + a + ', ' + b
		print_ttest(g1,g2, ttest_ind)
