import sqlite3, sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

# add modeling module
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
from models import Packer
import utils

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT participant, stimulus from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

# assumed distribution of range differential
sig = 0.2

# make a template df
template_df = pd.DataFrame(utils.cartesian([[0,1], range(stimuli.shape[0])]), 
	columns = ['condition', 'stimulus'])
for i, c in enumerate(pd.unique(info.condition)):
	template_df.loc[template_df.condition == i, 'condition'] = c
template_df['drange'] = 0
template_df['size'] = 0
template_df['stimulus'] = template_df['stimulus'].astype(int)

# condition, stimulus, mean, variance, n

# fill out template with behavioral data
observed = template_df.copy()
generation = pd.merge(generation, stats[['participant', 'drange']],    on='participant')
for (c,n), rows in observed.groupby(['condition', 'stimulus']):
	pids = info.loc[info.condition == c, 'participant']
	
	g_idx = generation.participant.isin(pids) & (generation.stimulus == n)
	trials = generation.loc[g_idx, 'drange']
	if trials.shape[0] == 0: continue

	o_idx = (observed.condition == c) & (observed.stimulus == n)
	observed.loc[o_idx, 'drange'] = np.sum(trials)
	observed.loc[o_idx, 'size'] = trials.shape[0]

# params for PACKER
params = dict(
        specificity = 0.562922970884,
        between = 1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )

nsamples = 50

simulated = template_df.copy()
for i, row in stats.groupby('participant'):
	pcond = info.loc[info.participant == i, 'condition'].iloc[0]
	As = stimuli[alphas[pcond],:]

	# get weights
	rs = np.array(row[['xrange','yrange']])[0]
	rs = 1.0 / (rs + 1.0/9.0)
	params['wts'] = rs / float(np.sum(rs))
	# params['wts'] = np.array([0.5, 0.5])

	model = Packer([As], params)
	for j in range(nsamples):	

		nums = model.simulate_generation(stimuli, 1, nexemplars = 4)
		model.forget_category(1)

		ranges = np.ptp(stimuli[nums,:], axis = 0)
		drange = ranges[0] - ranges[1]

		idx = (simulated.condition == pcond) & simulated.stimulus.isin(nums)
		simulated.loc[idx, 'drange'] += drange
		simulated.loc[idx, 'size'] += 1



# plotting
f, ax = plt.subplots(2,2,figsize = (5,5))
for colnum, c in enumerate(pd.unique(info.condition)):
	A = stimuli[alphas[c],:]
	for j, data in enumerate([observed, simulated]):
		h = ax[j][colnum]
		df = data.loc[data.condition == c]

		x = stimuli[df.stimulus,0]
		y = stimuli[df.stimulus,1]
		

		sumx = df.drange.as_matrix()
		n = df['size'].as_matrix()
		vals  = (0.0/sig +  sumx / sig) / (1.0/sig + n / sig)
		vals = (vals + 2.0) / 4.0

		print c, j, min(vals), max(vals)

		alpha = 1.
		# if j==1: alpha /= nsamples

		h.scatter(x, y, c=vals, 
			s=235,alpha = 0.2, marker = 's', 
			edgecolors = 'gray', linewidth = 0.5,
			cmap = 'PuOr')

# plot alphas
fontsettings = dict(fontsize = 12.0)
for i in range(2):
	for colnum, j in enumerate(pd.unique(info.condition)):
		h = ax[i][colnum]
		utils.plotclasses(h, stimuli, alphas[j], [])

		if colnum == 0:
				if i== 0:
					h.set_ylabel('Behavioral', rotation = 0, ha = 'right', **fontsettings)
				if i == 1:
					h.set_ylabel('PACKER', rotation = 0, ha = 'right', **fontsettings)

		if i==0:
			h.set_title(j, **fontsettings)

plt.tight_layout(pad=0.0, w_pad=0.3, h_pad= -4.0)
f.savefig('range.x.location.png', bbox_inches='tight', transparent=False)


