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

# get observed data
observed = pd.DataFrame(generation)
observed['F1'] = stimuli[observed.stimulus,0]
observed['F2'] = stimuli[observed.stimulus,1]
observed = pd.merge(observed, stats[['participant', 'drange']],    on='participant')
observed.drange = (observed.drange + 2.0) / 4.0

# params for PACKER
params = dict(
        specificity = 0.562922970884,
        between = 1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )

simulated = pd.DataFrame(dict(
	participant = observed['participant'],
	stimulus = None,
	drange = None),
	index = observed.index
)

for i, row in stats.groupby('participant'):
	pcond = info.loc[info.participant == i, 'condition'].iloc[0]
	As = stimuli[alphas[pcond],:]

	# get weights
	rs = np.array(row[['xrange','yrange']])[0]
	rs = 1.0 / (rs + 1.0/9.0)
	params['wts'] = rs / float(np.sum(rs))

	model = Packer([As], params)
	nums = model.simulate_generation(stimuli, 1, nexemplars = 4)
	ranges = np.ptp(stimuli[nums,:], axis = 0)
	drange = ((ranges[0] - ranges[1]) + 2.0) / 4.0

	idx = simulated.participant == i
	simulated.loc[idx, 'stimulus'] = nums
	simulated.loc[idx, 'drange'] = drange

simulated['F1'] = stimuli[simulated.stimulus,0]
simulated['F2'] = stimuli[simulated.stimulus,1]

def d2color(vec):
	d = np.array(vec)
	static = np.zeros(len(d))
	return np.array([d, d, static]).T

def plotbs(h, Bs, color):
	pts = utils.jitterize(Bs, sd = 0.05)
	for i, row in enumerate(pts):
		h.plot(row[0], row[1], 'o', 
			color = color[i,:], 
			alpha = 0.4, 
			markersize = 7,
			markeredgecolor = 'none')

# plot betas
f, ax = plt.subplots(2,2,figsize = (5,5))
for colnum, c in enumerate(pd.unique(info.condition)):

	# get rows
	pids = info.loc[info.condition == c, 'participant']
	obs = observed.loc[observed.participant.isin(pids)]
	sim = simulated.loc[simulated.participant.isin(pids)]

	dfs = [observed, simulated]
	for j in range(2):
		df = dfs[j].loc[dfs[j].participant.isin(pids)]
		Bs = df[['F1','F2']].as_matrix()
		colors = d2color(df.drange)
		h = ax[j][colnum]
		plotbs(h, Bs, colors)



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


