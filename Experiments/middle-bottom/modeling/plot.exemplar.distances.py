import sqlite3
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option('precision', 3)
np.set_printoptions(precision = 3)

# grab behavioral data
con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT participant, condition from participants", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

# import modeling modules
execfile('Imports.py')
from Modules.Classes import Packer, CopyTweak, ConjugateJK13, Optimize
import Modules.Funcs as funcs

# get best params for each model
with open( "best.params.pickle", "rb" ) as f:
	best_params = pickle.load( f )

# set up storage
N = 200
results = []

# simulate generation
for i, model_obj in enumerate([Packer, CopyTweak, ConjugateJK13]):
	params = best_params[model_obj.model]

	for j, condition in enumerate(pd.unique(participants.condition)):
		As = stimuli[alphas[condition],:]
		cond_obj = model_obj([As], params)

		for k in range(N):
			betas = cond_obj.simulate_generation(stimuli, 1, nexemplars = 4)
			cond_obj.forget_category(1)

			for b in betas:
				results.append(dict( model = model_obj.model,	condition = condition, participant = k, stimulus = b	))


results = pd.DataFrame(results)

f, ax = plt.subplots(1, 3, figsize = (6.5,2))
styles = dict(Middle = '-o', Bottom = '-s')
colors = dict(Middle = 'orange', Bottom = 'purple')

for axnum, (modelname, modelrows) in enumerate(results.groupby('model')):
	h = ax[axnum]
	for condition, rows in modelrows.groupby('condition'):
		
		As = stimuli[alphas[condition],:]
		D = funcs.pdist(stimuli, As)
		D = np.mean(D, axis = 1)
		x = np.unique(D)
		y = []
		for j in x:
			nums = np.where(D == j)[0]
			curr_rows = rows.loc[rows.stimulus.isin(nums)]
			counts = curr_rows.groupby('stimulus').agg('size')
			y.append(np.mean(counts) * (61.0 / N))

		x = x - min(x)
		x = x / max(x)
		h.plot(x, y, styles[condition], color = colors[condition], alpha = 0.7, label = condition)

	h.set_title(modelname, fontsize = 11)
	h.yaxis.grid(True)
	h.set_xticks([])

	if axnum == 0:
		h.set_ylabel('Generations Per Stimulus', fontsize = 10)

	if axnum == 1:
		h.legend(loc = 'upper left', frameon = True, framealpha = 1, fontsize = 9)

	h.set_yticks(np.arange(0,35, 5))
	h.set_yticklabels(np.arange(0,35, 5),fontsize = 9)
	if axnum > 0:
		h.set_yticklabels([],fontsize = 9)

	xax = h.axis()
	h.text(xax[0],xax[2] -1, 'Min', fontsize = 9, va = 'top')
	h.text(xax[1],xax[2] -1, 'Max', fontsize = 9, va = 'top', ha = 'right')
	h.set_xlabel('Distance')
	
	

f.savefig('exemplar.distance.png', bbox_inches = 'tight', pad_inches=0.0)









