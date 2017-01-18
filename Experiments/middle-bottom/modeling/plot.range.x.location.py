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

nstimuli = stimuli.shape[0]

# get observed dataframe
# condition, stimulus, mean, var, size
observed = pd.merge(generation, stats[['participant', 'drange']], on='participant')
observed = pd.merge(observed, info[['participant', 'condition']], on='participant')
observed = observed.groupby(['condition','stimulus'])['drange'].agg(['mean', 'var', 'size'])
observed = observed.reset_index()
observed.loc[pd.isnull(observed['var']),'var'] = 1.0


# params for PACKER
params = dict(
        specificity = 0.562922970884,
        between = 1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )

nsamples = 40

# get simulated data
simulated = pd.DataFrame(dict(condition = [], stimulus = [], drange = []))
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

		rows = dict(condition = [pcond] *4, stimulus = nums, drange = [drange] *4)
		simulated = simulated.append(pd.DataFrame(rows), ignore_index = True)

simulated = simulated.groupby(['condition','stimulus'])['drange'].agg(['mean', 'var', 'size'])
simulated = simulated.reset_index()
simulated.loc[pd.isnull(simulated['var']),'var'] = 1.0
simulated['size'] /= nsamples


scatter_settings = dict(s = 220, alpha = 1.0, marker = 's', 
			edgecolors = 'gray', linewidth = 0.5, cmap = 'PuOr',
			vmin = -2, vmax = 2)

from scipy.interpolate import interp2d

# plotting
f, ax = plt.subplots(2,2,figsize = (5,5))
for colnum, c in enumerate(pd.unique(info.condition)):
	A = stimuli[alphas[c],:]
	for j, data in enumerate([observed, simulated]):
		h = ax[j][colnum]
		df = data.loc[data.condition == c]

		# get x/y pos of examples
		nums = df.stimulus.as_matrix().astype(int)
		x = stimuli[nums,0]
		y = stimuli[nums,1]
	
		# compute color
		n = df['size'].as_matrix()
		sumx = df['mean'].as_matrix() * n
		sig = df['var'].as_matrix()
		sig[sig==0] = 0.01
		vals  = (0.0/sig +  sumx / sig) / (1.0/sig + n/sig)

		print c, j, min(vals), max(vals)
		h.scatter(x, y, c=vals, **scatter_settings)
		
		# plot missing items as white squares
		missing = [i for i in range(nstimuli) if i not in nums]
		x = stimuli[missing,0]
		y = stimuli[missing,1]
		vals = [0.0 for i in missing]
		h.scatter(x, y, c = vals, **scatter_settings)
		


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


