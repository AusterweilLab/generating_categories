import pickle
import pandas as pd

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Optimize
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

best_fits = dict()
for model_obj in [CopyTweak, Packer, ConjugateJK13]:
# for o in [ConjugateJK13]:

	inits = model_obj.rvs(fmt = list)

	print '\nInit values:'
	print dict(zip(model_obj.parameter_names, [round(i,3) for i in inits]))

	res = Optimize.hillclimber(model_obj, inits, trials, options)
	dummy_model = model_obj(None, res.x)
	best_fits[model_obj.model] = dummy_model.params


