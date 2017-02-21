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

	ax.set_title(col)
	ax.set_ylabel('')

	if 'range' in col:
		ax.set_title(col[0].upper() + ' Range')
	else:
		ax.set_title('Correlation', fontsize = 14)

	ax.tick_params(labelsize = 12)
	ax.set_xlabel('')
	ax.xaxis.grid(False)

fh.savefig('statsboxes.png', bbox_inches = 'tight', pad_inches=0.0)


# hypothesis tests
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp

def print_ttest(g1, g2, fun):
	res = fun(g1,g2)
	S = 'T = ' + str(round(res.statistic, 4))
	S+= ', p = ' + str(round(res.pvalue, 4))
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
