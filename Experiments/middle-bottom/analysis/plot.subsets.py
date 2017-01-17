import sqlite3, sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

sys.path.insert(0, "../../../Modules/")
import utils

np.set_printoptions(precision = 2)
pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
betas = pd.read_sql_query("SELECT participant, stimulus from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

savedir = 'subsets'
data = pd.merge(stats, info[['participant','condition']], on = 'participant')

fields = ['top_and_bottom', 'bottom_only', 'top_only', 'bottom_used', 'top_used']



for cstring, condition in data.groupby('condition'):
	As = stimuli[alphas[cstring],:]
	for F in fields:
		for v, rows in condition.groupby(F):
			if rows.shape[0] < 5: continue
			pids = rows.participant
			Bs = betas.loc[betas.participant.isin(pids), 'stimulus'].as_matrix()
			
			g = np.empty((stimuli.shape[0]))
			for j in range(stimuli.shape[0]):
				g[j] = sum(Bs==j)
			g = g / float(sum(g))
			g = utils.gradientroll(g,'roll')[:,:,0]
			print np.max(g)

			f = plt.figure(figsize = (3,3))
			fname = savedir + '/' + cstring + '-' + F + '-' + str(v) + '.png'
			utils.plotgradient(f.gca(), g, As, [], clim = (0, 0.2))
			plt.title('n = ' + str(rows.shape[0]))
			f.savefig(fname, bbox_inches='tight', transparent=False)