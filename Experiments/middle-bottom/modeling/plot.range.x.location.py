import sqlite3, sys
import numpy as np
import pandas as pd

from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt

# add modeling module
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
from models import Packer, CopyTweak, ConjugateJK13
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
model_param_pairs = [
    [CopyTweak, dict(
        specificity = 9.4486327043,
        within_pref = 17.0316650379,
        tolerance = 0.403108523886,
        determinism = 7.07038770338,
        )],
    [Packer, dict(
        specificity = 0.562922970884,
        between = -1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )],
    [ConjugateJK13, dict(
        category_mean_bias = 0.0167065365661,
        category_variance_bias = 1.00003245067,
        domain_variance_bias = 0.163495499745,
        determinism = 2.10276377982,
        )],
]

model_obj, params = model_param_pairs[1]
nsamples = 50

# get simulated data
simulated = pd.DataFrame(dict(condition = [], stimulus = [], drange = []))
for i, row in stats.groupby('participant'):
	pcond = info.loc[info.participant == i, 'condition'].iloc[0]
	As = stimuli[alphas[pcond],:]

	# get weights
	rs = np.array(row[['xrange','yrange']])[0]
	params['wts'] = rs / float(np.sum(rs))
	# params['wts'] = np.array([0.5, 0.5])

	model = model_obj([As], params)
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




# plotting
fontsettings = dict(fontsize = 10.0)

f, ax = plt.subplots(2,2,figsize = (3.5,3.5))
for colnum, c in enumerate(pd.unique(info.condition)):
	A = stimuli[alphas[c],:]
	
	for j, data in enumerate([observed, simulated]):
		h = ax[j][colnum]
		df = data.loc[data.condition == c]

		# get x/y pos of examples
		x, y = stimuli[:,0], stimuli[:,1]
	
		# compute colors
		vals = np.zeros(nstimuli)
		for i, row in df.groupby('stimulus'):
			n = row['size'].as_matrix()
			sumx = row['mean'].as_matrix() * n
			sig = row['var'].as_matrix()
			if sig == 0: 
				sig = 0.001
			vals[int(i)] = (0.0/sig +  sumx / sig) / (1.0/sig + n/sig)

		print c, j, min(vals), max(vals)

		# smoothing
		g = utils.gradientroll(vals,'roll')[:,:,0]
		g = gaussian_filter(g, 0.8)
		vals = utils.gradientroll(g,'unroll')
		
		im = utils.plotgradient(h, g, A, [], clim = (-2, 2), cmap = 'PuOr')

		# axis labelling
		if colnum == 0:
			lab = ['Behavioral', model_obj.model][j]
			h.set_ylabel(lab, rotation = 0, ha = 'right', va = 'center', **fontsettings)

		if j == 0:
			h.set_title(c, fontsize = 12.0)



# add colorbar
cbar = f.add_axes([0.375, 0.05, 0.45, 0.05])
f.colorbar(im, cax=cbar, ticks=[-2, 2], orientation='horizontal')
cbar.set_xticklabels([
	'Vertically\nAligned Category', 
	'Horizontally\nAligned Category', 
],**fontsettings)
cbar.tick_params(length = 0)



plt.tight_layout(w_pad=0.3, h_pad= -4.0)
f.savefig('range.x.location.png', bbox_inches='tight', transparent=False)

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
f.savefig('../../../Manuscripts/cogsci-2017/figs/range-diff-gradient.pgf', bbox_inches='tight')
