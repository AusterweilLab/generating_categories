import sqlite3, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.set_printoptions(precision = 2)
sys.path.insert(0, "../../../Modules/")
import utils



con = sqlite3.connect('../data/experiment.db')
infodf = pd.read_sql_query("SELECT * from participants", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
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
	g = utils.gradientroll(ps,'roll')[:,:,0]

	# g = gaussian_filter(g, 0.8)

	print(g)
	print(K, np.max(g))

	h = ax[i]
	im = utils.plotgradient(h, g, stimuli[alphas[K],:], [], clim = clim)
	h.set_title(K, fontsize = 12)


# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.225, 0.03, 0.54])
f.colorbar(im, cax=cbar, ticks = clim)
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
f.savefig('../../../Manuscripts/cogsci-2017/figs/behavioral-heatmaps.pgf',	bbox_inches='tight')

f.savefig('heatmaps.png', bbox_inches='tight', transparent=False)

