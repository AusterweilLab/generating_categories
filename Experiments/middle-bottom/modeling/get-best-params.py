import pickle

execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13, Optimize
import Modules.Funcs as funcs


# get data from pickle
with open( "data.pickle", "rb" ) as f:
	trials, stimuli = pickle.load( f )


# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 


best_fits = dict()
for model_obj in [CopyTweak, Packer, ConjugateJK13]:
# for o in [ConjugateJK13]:

	inits = model_obj.rvs()

	print '\nInit values:'
	print dict(zip(model_obj.parameter_names, [round(i,3) for i in inits]))

	res = Optimize.hillclimber(model_obj, inits, trials, stimuli, options)

	dummy_model = model_obj(None, res.x)
	best_fits[model_obj.model] = dummy_model.params

# save to pickle
with open('best.params.pickle','wb') as f:
	pickle.dump(best_fits, f)
