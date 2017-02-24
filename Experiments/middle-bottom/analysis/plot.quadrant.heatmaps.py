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
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT * from generation", con)
con.close()

stats = pd.merge(stats, info, on = 'participant')
generation = pd.merge(generation, info, on = 'participant')

# get profiles
stats['profile'] = pd.Series(None, index = stats.index)
idx = (stats['xrange'] < 1) & (stats['yrange'] < 1)
stats.loc[idx,'profile'] = 'Cluster' # cluster

idx = (stats['xrange'] > 1) & (stats['yrange'] < 1)
stats.loc[idx,'profile'] = 'Row' # row

idx = (stats['xrange'] < 1) & (stats['yrange'] > 1)
stats.loc[idx,'profile'] = 'Column' # col

idx = (stats['xrange'] > 1) & (stats['yrange'] > 1)
stats.loc[idx,'profile'] = 'Corners' # cluster / xor

print pd.pivot_table(stats, index = 'profile', columns = 'condition', 
	values = 'participant', aggfunc = 'count')



generation = pd.merge(generation, stats[['participant','profile']], on = 'participant')
clim = (0.0, 0.12)
from scipy.ndimage.filters import gaussian_filter



f, axes = plt.subplots(2,4,figsize = (8, 4))
axes = axes.flatten()
for i, ((c, p), rows) in enumerate(generation.groupby(['condition','profile'])):
	ax = axes[i]
	betas = rows.stimulus.as_matrix()

	counts = np.array([sum(betas==j) for j in range(stimuli.shape[0])])
	ps = counts / float(sum(counts))
	g = funcs.gradientroll(ps,'roll')[:,:,0]
	g = gaussian_filter(g, 0.8)
	print np.max(g)

	im = funcs.plotgradient(ax, g, stimuli[alphas[c],:], [], clim = clim)

	S = p + ', n = ' + str(rows.shape[0] / 4)
	ax.set_title(S, fontsize = 12)
	if i in [0, 4]:	ax.set_ylabel(c)

# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.225, 0.03, 0.54])
f.colorbar(im, cax=cbar, ticks = clim)
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)

f.savefig('quadrant-heatmaps.png', bbox_inches='tight', transparent=False)


