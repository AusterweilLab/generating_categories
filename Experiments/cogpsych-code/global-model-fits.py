import pickle
import pandas as pd

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13

# get trials pickle
# get data from pickle
with open("pickles/all_data_e1_e2.p", "rb" ) as f:
	trials = pickle.load( f )


# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 

results = dict()
for model_obj in [CopyTweak, Packer, ConjugateJK13]:

	res = Simulation.hillclimber(model_obj, trials, options)
	X = model_obj.params2dict(model_obj.clipper(res.x))
	results[model_obj.model] = X

# save final result in pickle
with open('pickles/best_params_e1_e2.p','wb') as f:
	pickle.dump(results, f)

for k,v in results.items():
	print k, v