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


# define top and bottom IDs, number of participants
bottom_nums = range(9)
top_nums = range(72,81)
N = 61

# set up storage
results = pd.DataFrame(dict(
	model = [],
	condition = [],
	participant = [],
	top_used = [],
	bottom_used = [],
	top_and_bottom = [],
	))

for i, model_obj in enumerate([Packer, CopyTweak, ConjugateJK13]):
	params = best_params[model_obj.model]

	for j, condition in enumerate(pd.unique(participants.condition)):
		As = stimuli[alphas[condition],:]
		cond_obj = model_obj([As], params)

		for k in range(N):
			betas = cond_obj.simulate_generation(stimuli, 1, nexemplars = 4)
			cond_obj.forget_category(1)

			bottom_used = np.any(np.in1d(betas,bottom_nums))
			top_used = np.any(np.in1d(betas,top_nums))
			top_and_bottom = (bottom_used == True) & (top_used == True)
			row = dict(
				model = model_obj.model,
				condition = condition,
				participant = k,
				top_used = top_used,
				bottom_used = bottom_used,
				top_and_bottom = top_and_bottom,
				)
			results = results.append(row, ignore_index = True)

g = results.groupby(['model', 'condition'])
for (m, c), rows in g:
	print '\n----------------'
	print m + ' -- ' + c
	print pd.pivot_table(rows, index = 'bottom_used', columns = 'top_used', aggfunc = 'size', fill_value = 0)
