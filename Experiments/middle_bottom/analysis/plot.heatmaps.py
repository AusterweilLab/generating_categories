import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os,sys
os.chdir(sys.path[0])


np.set_printoptions(precision = 2)

exec(open('Imports.py').read())
import Modules.Funcs as funcs



con = sqlite3.connect('../data/experiment.db')
infodf = pd.read_sql_query("SELECT * from participants", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()
alphas = pd.read_sql_query("SELECT * from alphas", con)
generation = pd.read_sql_query("SELECT * from generation", con)
con.close()

from scipy.ndimage.filters import gaussian_filter

clim = (0.0, 0.10)

f, ax = plt.subplots(1,2, figsize = (4,2))
for i, (K, rows) in enumerate(infodf.groupby('condition')):

	pids = rows.participant
	betas = generation.loc[generation.participant.isin(pids), 'stimulus']
	
	counts = np.array([sum(betas==j) for j in range(stimuli.shape[0])])
	ps = counts / float(sum(counts))
	g = funcs.gradientroll(ps,'roll')[:,:,0]

	# g = gaussian_filter(g, 0.8)

	print(g)
	print(K, np.max(g))

	h = ax[i]
	im = funcs.plotgradient(h, g, stimuli[alphas[K],:], [], clim = clim)
	h.set_title(K, fontsize = 12)


# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.225, 0.03, 0.54])
f.colorbar(im, cax=cbar, ticks = clim)
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)

f.savefig('heatmaps.pdf', bbox_inches='tight', transparent=False)

path = '../../../Manuscripts/cogsci-2017/figs/behavioral-heatmaps.pgf'
# funcs.save_as_pgf(f, path)


