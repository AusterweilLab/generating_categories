import pickle
import pandas as pd

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13

# Specify default dataname
dataname_def = 'pooled-no1st'

#Allow for input arguments at the shell
if __name__ == "__main__":
        import sys
        
        if len(sys.argv)<2:
                dataname = dataname_def
        else:
                dataname = sys.argv[1]        
else:
        dataname = dataname_def



# Data
if dataname == 'pooled':
        # all data
        src = "pickles/all_data_e1_e2.p"
        dst = "pickles/best_params_all_data_e1_e2.p"
        task = "generate"
elif dataname == 'pooled-no1st':
        # trials 2-4
        src = "pickles/trials_2-4_e1_e2.p"
        dst = "pickles/best_params_trials_2-4_e1_e2.p"
        task = "generate"
elif dataname == 'nosofsky1986':
        # nosofsky data
        src = "pickles/nosofsky1986.p"
        dst = "pickles/best_params_nosofsky1986.p"
        task = "assign"
else:
        raise Exception('Invalid data name specified.')

print 'Fitting Data: ' + dataname

# get data from pickle
with open(src, "rb" ) as f:
	trials = pickle.load( f )

trials.task = task

print trials

# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 

results = dict()
for model_obj in [ConjugateJK13, CopyTweak, Packer]:
	res = Simulation.hillclimber(model_obj, trials, options)
	X = model_obj.params2dict(model_obj.clipper(res.x))
	results[model_obj.model] = X

# save final result in pickle
with open(dst,'wb') as f:
	pickle.dump(results, f)

for k,v in results.items():
	print k, v



