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
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')
generation = pd.merge(generation, info, on = 'participant')

ngenerations = pd.DataFrame(dict(
	condition = [],
	stimulus = [],
	count = []
))

for c in pd.unique(info.condition):
	for i in range(stimuli.shape[0]):
		count = sum((generation.condition == c) & (generation.stimulus ==i))
		row = dict(condition = c, stimulus = i, count = count)
		ngenerations = ngenerations.append(row, ignore_index = True)


fh, ax = plt.subplots(1,2,figsize = (6,2.7))

styles = dict(XOR = '-^',	Cluster = '-o', Row = '-s')

h = ax[0]
for i, (c, rows) in enumerate(ngenerations.groupby('condition')):

	As = stimuli[alphas[c],:]
	D = funcs.pdist(stimuli, As)
	D = np.mean(D, axis = 1)
	x = np.unique(D)
	y = []
	for j in x:
		nums = np.where(D == j)[0]
		curr_rows = rows.loc[rows.stimulus.isin(nums)]
		counts = curr_rows['count'].as_matrix()
		y.append(np.mean(counts))

	x = x - min(x)
	x = x / max(x)
	h.plot(x, y, styles[c], alpha = 0.7, label = c)

h.xaxis.grid(False)
h.set_xticks([])
h.legend(loc = 'upper left', frameon = True, framealpha = 1, fontsize = 10)


xax = h.axis()
h.text(xax[0],xax[2] -1, 'Min', fontsize = 10, va = 'top')
h.text(xax[1],xax[2] -1, 'Max', fontsize = 10, va = 'top', ha = 'right')
h.set_xlabel('Distance', fontsize = 12)
# h.set_yticks(np.arange(0,12, 2))
# h.set_yticklabels(np.arange(0, 12, 2),fontsize = 10)
h.set_ylabel('Generations Per Stimulus', fontsize = 12)


h = ax[1]
styles = dict(XOR = '^',	Cluster = 'o', Row = 's')
h.plot([0,2],[0,2], '--', color = 'gray', linewidth = 0.5, label = 'Within $=$ Between')

for c, rows in stats.groupby('condition'):
	h.plot(rows.within, rows.between, styles[c],
		alpha = 0.5, label = '')

h.grid(False)


h.set_xticks([])
h.set_yticks([])

h.axis([0, 1.5, 0, 1.5])
h.set_xlabel('Within-Class Distance',fontsize = 12)
h.set_ylabel('Between-Class Distance',fontsize = 12)

fh.subplots_adjust(wspace=0.3)
# plt.tight_layout(pad = 0.5)


fname = 'distance.figs'
fh.savefig(fname + '.pdf', bbox_inches = 'tight', pad_inches=0.0)

path = '../../../Manuscripts/cog-psych/figs/e1-distanceplots.pgf'
funcs.save_as_pgf(fh, path)


		