import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.set_printoptions(precision = 2)
pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con)
con.close()


stats = pd.merge(stats, info[['participant', 'condition']], on = 'participant')
df = pd.merge(df, info[['participant', 'condition']], on = 'participant')
df['y'] = stimuli.loc[df.stimulus, 'F2'].as_matrix()
df['x'] = stimuli.loc[df.stimulus, 'F1'].as_matrix()

def plotlines(h, data, stats):
	sort_df = stats.sort_values(by = ['yrange','condition'])
	condition_colors = dict(Middle = 'r', Bottom = 'b')
	n = 0

	for num, info in sort_df.iterrows():
		pid = info.participant
		g = info.condition

		rows = data.loc[data.participant == pid]

		# plot lines
		x = [n for i in range(2)]
		y = np.array([np.min(rows.y), np.max(rows.y)])
		h.plot(x, y, '-', alpha = 0.8,
			color = condition_colors[g])

		# plot examples
		x = [n for i in range(4)]
		y = np.array(rows.y)
		h.plot(x,y, '.', markersize = 4,
			fillstyle = 'full',
			markeredgecolor = condition_colors[g],
			color = condition_colors[g],
			alpha = 1)		
		n += 1



	h.axis([-1.5, stats.shape[0] + 0.5,  -1.05, 1.05])
	h.set_yticks([])
	h.set_xticks([])
	h.set_ylabel('Y Axis Value', fontsize = 11)
	h.set_xlabel('Y-Axis Range', fontsize = 11)

	for k, v in condition_colors.items():
		plt.plot(np.NaN, np.NaN, '-', color = v, label = k)
	h.legend(loc="center left", fontsize = 11, frameon=False)


fh = plt.figure(figsize = (8,2))
plotlines(fh.gca(), df, stats)
[i.set_linewidth(1.0) for i in fh.gca().spines.itervalues()]


fh.savefig('yranges.png', bbox_inches = 'tight')

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
fh.savefig('../../../Manuscripts/cogsci-2017/figs/middle-bottom-yranges.pgf',
	bbox_inches='tight')