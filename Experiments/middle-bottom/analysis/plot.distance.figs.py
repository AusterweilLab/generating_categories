import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

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



fh, ax = plt.subplots(2,1,figsize = (3.5,5.5))
condition_styles = dict(Middle = 'r-o', Bottom = 'b-s')

h = ax[0]
for i, (c, rows) in enumerate(ngenerations.groupby('condition')):

	As = stimuli[alphas[c],:]
	D = utils.pdist(stimuli, As)
	D = np.mean(D, axis = 1)
	x = np.unique(D)
	y = []
	for j in x:
		nums = np.where(D == j)[0]
		curr_rows = rows.loc[rows.stimulus.isin(nums)]
		counts = curr_rows['count'].as_matrix()
		y.append(np.mean(counts))
	print y

	x = x - min(x)
	x = x / max(x)
	h.plot(x, y, condition_styles[c], alpha = 0.7, label = c)

h.xaxis.grid(False)
h.set_xticks([])
h.legend(loc = 'upper left', frameon = True, framealpha = 1)


xax = h.axis()
h.text(xax[0],xax[2] -1, 'Min Distance', fontsize = 10, va = 'top')
h.text(xax[1],xax[2] -1, 'Max Distance', fontsize = 10, va = 'top', ha = 'right')

h.set_ylabel('Generations Per Stimulus')


h = ax[1]
condition_styles = dict(Middle = 'ro', Bottom = 'bs')
h.plot([0,2],[0,2], '--', color = 'gray', linewidth = 0.5, label = 'Within = Between')
for c, rows in stats.groupby('condition'):
	h.plot(rows.within, rows.between, condition_styles[c], 
		alpha = 0.5, label = c)
h.grid(False)


h.set_xticks([])
h.set_yticks([])

h.axis([0, 2, 0, 2])
h.legend(loc = 'upper right', frameon = True, framealpha = 1, 
	ncol = 2, columnspacing = 0.1, labelspacing = 0.1)
h.set_xlabel('Within-Category Distance')
h.set_ylabel('Between-Category Distance')


plt.tight_layout(h_pad=2.0)


fname = 'distance.figs'

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
fh.savefig('../../../Manuscripts/cogsci-2017/figs/' + fname +'.pgf',	bbox_inches='tight')


fh.savefig(fname + '.png', bbox_inches = 'tight')


		