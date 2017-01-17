import sqlite3, sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

# add modeling module
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
from models import Packer
import utils


np.set_printoptions(precision = 2)
pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT participant, stimulus from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()


# params for PACKER
params = dict(
        specificity = 0.562922970884,
        between = 1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )

info.set_index('participant',inplace=True)
conditions = list(pd.unique(info.condition))



def plotbs(h, Bs, color):
	pts = utils.jitterize(Bs,sd = 0.1)
	h.plot(pts[:,0], pts[:,1], 'o', 
		color = color, 
		alpha = 0.4, 
		markeredgecolor = 'none')
fontsettings = dict(fontsize = 12.0)

f, ax = plt.subplots(2,2,figsize = (5,5))
for i, row in stats.groupby('participant'):
	pcond = info.loc[i, 'condition']

	rs = np.array(row[['xrange','yrange']])[0]
	rs = 1.0 / (rs + 1.0/9.0)

	d = (float(row.drange) + 2.0) / 4.0
	
	# get wts and beta color

	wts = rs / float(np.sum(rs))

	# wts = np.array([0.5, 0.5])
	color = [1-d, 1-d, d]

	colnum = conditions.index(pcond)
	h = ax[0][colnum]

	# plot behavioral data
	Bs = generation.loc[generation.participant == i, 'stimulus']
	Bs = stimuli[Bs,:]
	h = ax[0][conditions.index(pcond)]
	plotbs(h, Bs, color)

	h = ax[1][colnum]
	params['wts'] = wts
	model = Packer([stimuli[alphas[pcond],:]], params)
	nums = model.simulate_generation(stimuli, 1, nexemplars = 4)
	simulated_Bs = stimuli[nums,:]
	rs = np.ptp(simulated_Bs,axis=0)
	d = (float(rs[0] - rs[1]) + 2.0) / 4.0
	color = [1-d, 1-d, d]
	plotbs(h, simulated_Bs, color)

# add alphas
for i in range(2):
	for j in conditions:
		colnum = conditions.index(j)
		h = ax[i][conditions.index(j)]
		utils.plotclasses(h, stimuli, alphas[j], [])

		if colnum == 0:
				if i== 0:
					h.set_ylabel('Behavioral', rotation = 0, ha = 'right', **fontsettings)
				if i == 1:
					h.set_ylabel('PACKER', rotation = 0, ha = 'right', **fontsettings)

		if i==0:
			h.set_title(j, **fontsettings)


f.savefig('range.x.location.png', bbox_inches='tight', transparent=False)


