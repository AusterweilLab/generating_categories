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

f, ax = plt.subplots(1,2, figsize = (4,2))
counter = 0
for i, rows in infodf.groupby('condition'):

	pids = rows.participant
	betas = generation.loc[generation.participant.isin(pids), 'stimulus']
	
	counts = np.array([sum(betas==j) for j in range(stimuli.shape[0])])
	ps = counts / float(sum(counts))
	g = utils.gradientroll(ps,'roll')[:,:,0]

	print(g)
	print(i, np.max(g))

	h = ax[counter]
	utils.plotgradient(h, g, stimuli[alphas[i],:], [], clim = (0.0, 0.15))
	counter += 1


import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
f.savefig('../../../Manuscripts/cogsci-2017/figs/behavioral-heatmaps.pgf',	bbox_inches='tight')

f.savefig('heatmaps.png', bbox_inches='tight', transparent=False)

