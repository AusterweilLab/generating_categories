import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
os.chdir(sys.path[0])
sns.set_style("whitegrid")

pd.set_option('display.width', 1000)
pd.set_option('display.precision', 2)


exec(open('Imports.py').read())
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')


fh, axes = plt.subplots(1,3,figsize = (7.5,2.5))
for i, col in enumerate(['xrange','yrange','correlation']):
	ax = axes[i]
	sns.factorplot(x = 'condition', y = col, data= stats, ax = ax, kind = 'box', 
		order = ['Cluster', 'Row','XOR'])

	ax.set_title(col, fontsize = 12)
	ax.set_ylabel('')

	if 'range' in col:
		ax.set_title(col[0].upper() + ' Range', fontsize = 12)

		ax.set_yticks([0,2])
		ax.set_yticklabels(['Min','Max'])

	else:
		ax.set_title('Correlation', fontsize = 12)
		ax.set_yticks([-1,-0.5,0,0.5,1])
		ax.set_yticklabels(['-1','-0.5','0','0.5','1'])
	ax.tick_params(labelsize = 11)
	ax.set_xlabel('')
	ax.xaxis.grid(False)

fh.subplots_adjust(wspace=0.4)
fh.savefig('statsboxes.pdf', bbox_inches = 'tight')

# path = '../../../Manuscripts/cog-psych/figs/e1-statsboxes.pgf'
# funcs.save_as_pgf(fh, path)


# hypothesis tests
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp, wilcoxon
from itertools import combinations

def print_ttest(g1, g2, fun):
	res = fun(g1,g2)
	S = 'T = ' + str(round(res.statistic, 4))
	S+= ', p = ' + str(round(res.pvalue, 10))
	S+= '\tMeans:'
	for j in [g1, g2]:
		S += ' ' + str(round(np.mean(j), 4))
		S +=  ' (' + str(round(np.std(j), 4)) + '),'
	print(S)


print('\n---- Row X vs. Y:')
g1 = stats.loc[stats.condition == 'Row', 'xrange']
g2 = stats.loc[stats.condition == 'Row', 'yrange']
print_ttest(g1,g2, ttest_rel)

print('\n---- Cluster X vs. Y:')
g1 = stats.loc[stats.condition == 'Cluster', 'xrange']
g2 = stats.loc[stats.condition == 'Cluster', 'yrange']
print_ttest(g1,g2, ttest_rel)

print('\n---- XOR X vs. Y:')
g1 = stats.loc[stats.condition == 'XOR', 'xrange']
g2 = stats.loc[stats.condition == 'XOR', 'yrange']
print_ttest(g1,g2, ttest_rel)

print('\n---- Cluster positive correlation?')
g1 = stats.loc[stats.condition == 'Cluster', 'correlation']
print(ttest_1samp(g1, 0).pvalue)
print(wilcoxon(g1).pvalue)

print('\n---- XOR negative correlation?')
g1 = stats.loc[stats.condition == 'XOR', 'correlation']
print_ttest(g1,0, ttest_1samp)
print(ttest_1samp(g1, 0).pvalue)
print(wilcoxon(g1).pvalue)

print('\n---- XOR has more total range than Cluster?')
g1 = stats.loc[stats.condition == 'Cluster', ['xrange','yrange']].sum(axis = 1)
g2 = stats.loc[stats.condition == 'XOR', ['xrange','yrange']].sum(axis = 1)
print_ttest(g1,g2, ttest_ind)

print('\n---- XOR has more total range than Row?')
g1 = stats.loc[stats.condition == 'Row', ['xrange','yrange']].sum(axis = 1)
g2 = stats.loc[stats.condition == 'XOR', ['xrange','yrange']].sum(axis = 1)
print_ttest(g1,g2, ttest_ind)


print('\n---- within vs. between?')
for n, rows in stats.groupby('condition'):
	print('\t'+n+':')
	g1 = rows.loc[:,'between']
	g2 = rows.loc[:,'within']
	print_ttest(g1,g2, ttest_rel)



# between conditions
for j in ['xrange','yrange','correlation']:
	for a, b in combinations(pd.unique(stats.condition), r=2):
		g1 = stats.loc[stats.condition == a, j]
		g2 = stats.loc[stats.condition == b, j]
		print('\n---- ' + ' ' + j + ': ' + a + ', ' + b)
		print_ttest(g1,g2, ttest_ind)

cols = ['condition', 'between', 'correlation', 'within', 'xrange', 'yrange']
print(stats[cols].groupby('condition').describe())
