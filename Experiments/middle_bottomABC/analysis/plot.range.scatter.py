import sqlite3, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
os.chdir(sys.path[0])

exec(open('Imports.py').read())
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')

# get alpha ranges
alpha_ranges = dict()
for j in alphas.columns:
	ranges = np.ptp(stimuli[alphas[j],:],axis=0)
	alpha_ranges[j] = dict(xrange = ranges[0], yrange = ranges[1])

f, axes = plt.subplots(1,2,figsize = (6, 3), sharey = True)
for i, (j, rows) in enumerate(stats.groupby('condition')):
	ar, ax = alpha_ranges[j], axes[i]

	x, y = rows['xrange'], rows['yrange']
	# x, y = [funcs.jitterize(i, sd = 0.05) for i in [x,y]]
	ax.plot(x,y,'o', markersize = 15, alpha = 0.5)

	x, y = ar['xrange'], ar['yrange']
	ax.plot(x,y,'ko', markersize = 25, markerfacecolor=(0, 0, 0, 0.5), lw = 10)
	ax.annotate(j, xy = (x+0.1,y+0.05), xytext = (x+0.45,y+0.2), fontsize = 14,
		arrowprops=dict(facecolor='black', headwidth = 10.1, alpha = 0.8))


	ax.set_title(j, fontsize = 14)
	ax.set_xlabel('X Axis Range', fontsize = 12)
	if i==0:	ax.set_ylabel('Y Axis Range', fontsize = 12)
	
	ax.axis([-0.2,2.2,-0.2,2.2])
	ax.set_xticklabels('')
	ax.set_yticklabels('')
	ax.xaxis.grid(False)
	ax.yaxis.grid(False)

f.subplots_adjust(wspace=0.1)
f.savefig('rangescatter.pdf', bbox_inches='tight', transparent=False)

