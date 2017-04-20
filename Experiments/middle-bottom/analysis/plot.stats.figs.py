import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
colors = ["#34495e", "#e74c3c"]
sns.set_palette(colors)


pd.set_option('display.width', 1000, 'precision', 2)


execfile('Imports.py')
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
	hs = sns.factorplot(x = 'condition', y = col, data= stats, ax = ax, kind = 'box', 
		order = ['Bottom', 'Middle'])

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
fh.savefig('statsboxes.png', bbox_inches = 'tight')

path = '../../../Manuscripts/cog-psych/figs/e2-statsboxes.pgf'
funcs.save_as_pgf(fh, path)

# hypothesis tests
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp, wilcoxon, ranksums
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


print '\n---- Bottom X vs. Y:'
g1 = stats.loc[stats.condition == 'Bottom', 'xrange']
g2 = stats.loc[stats.condition == 'Bottom', 'yrange']
print_ttest(g1,g2, ttest_rel)

print '\n---- Middle X vs. Y:'
g1 = stats.loc[stats.condition == 'Middle', 'xrange']
g2 = stats.loc[stats.condition == 'Middle', 'yrange']
print_ttest(g1,g2, ttest_rel)

print '\n---- Bottom positive correlation?'
g1 = stats.loc[stats.condition == 'Bottom', 'correlation']
print ttest_1samp(g1, 0).pvalue
print wilcoxon(g1).pvalue

print '\n---- within vs. between?'
for n, rows in stats.groupby('condition'):
	print '\t'+n+':'
	g1 = rows.loc[:,'between']
	g2 = rows.loc[:,'within']
	print_ttest(g1,g2, ttest_rel)

# between conditions
for j in ['xrange','yrange','correlation']:
	for a, b in combinations(pd.unique(stats.condition), r=2):
		g1 = stats.loc[stats.condition == a, j]
		g2 = stats.loc[stats.condition == b, j]
		print '\n---- ' + ' ' + j + ': ' + a + ', ' + b
		print_ttest(g1,g2, ttest_ind)

cols = ['condition', 'between', 'correlation', 'within', 'xrange', 'yrange']
print stats[cols].groupby('condition').describe()
