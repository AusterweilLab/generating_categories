import sqlite3
import numpy as np
import pandas as pd

from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt

# add modeling module
execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13, Optimize
import Modules.Funcs as funcs

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

nsamples = 2


model_param_pairs = {
    'Copy and\nTweak': [CopyTweak, dict(
        specificity = 9.4486327043,
        within_pref = 17.0316650379,
        tolerance = 0.403108523886,
        determinism = 7.07038770338,
        )],
    'PACKER': [Packer, dict(
        specificity = 0.562922970884,
        between = -1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )],
    'Heirarchical\nSampling': [ConjugateJK13, dict(
        category_mean_bias = 0.0167065365661,
        category_variance_bias = 1.00003245067,
        domain_variance_bias = 0.163495499745,
        determinism = 2.10276377982,
        )],
}

all_data = dict(Behavioral = observed)
for k, (model_obj, params) in model_param_pairs.items():
	print 'Running: ' + model_obj.model
	model_data = pd.DataFrame(dict(condition = [], stimulus = [], drange = []))

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
			model_data = model_data.append(pd.DataFrame(rows), ignore_index = True)

		print '\t' + str(i)

	model_data = model_data.groupby(['condition','stimulus'])['drange'].agg(['mean', 'var', 'size'])
	model_data = model_data.reset_index()
	model_data.loc[pd.isnull(model_data['var']),'var'] = 1.0
	model_data['size'] /= nsamples
	all_data[k] = model_data


# plotting
fontsettings = dict(fontsize = 9.0)

f, ax = plt.subplots(4,2,figsize = (3.3,5.5))
for colnum, c in enumerate(pd.unique(info.condition)):
	A = stimuli[alphas[c],:]
	
	for j, (lab, data) in enumerate(sorted(all_data.items())):
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
		g = funcs.gradientroll(vals,'roll')[:,:,0]
		g = gaussian_filter(g, 0.8)
		vals = funcs.gradientroll(g,'unroll')
		
		im = funcs.plotgradient(h, g, A, [], clim = (-2, 2), cmap = 'PuOr')

		# axis labelling
		if colnum == 0:
			h.set_ylabel(lab, rotation = 0, ha = 'right', va = 'center', **fontsettings)

		if j == 0:
			h.set_title(c, fontsize = 10.0)



# add colorbar
cbar = f.add_axes([0.38, -0.01, 0.45, 0.05])
f.colorbar(im, cax=cbar, ticks=[-2, 2], orientation='horizontal')
cbar.set_xticklabels([
	'Vertically\nAligned Category', 
	'Horizontally\nAligned Category', 
],**fontsettings)
cbar.tick_params(length = 0)



plt.tight_layout(w_pad=1.6, h_pad= -1.6)
f.savefig('range.x.location.png', bbox_inches='tight', transparent=False)

path = '../../../Manuscripts/cogsci-2017/figs/range-diff-gradient.pgf'
# funcs.save_as_pgf(f, path)

