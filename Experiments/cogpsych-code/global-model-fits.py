import pickle
import pandas as pd

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
import numpy as np

# seed rng
#np.random.seed(9001)

# Specify default dataname
dataname_def = 'nosofsky1986'#'pooled-no1st'#'nosofsky1986'#'NGPMG1994'
participant_def = 'all'
unique_trials_def = 'all'

#Allow for input arguments at the shell
if __name__ == "__main__":
        import sys

        if len(sys.argv)<4:
                unique_trials = unique_trials_def
        else:
                unique_trials = int(sys.argv[3])
        if len(sys.argv)<3:
                participant = participant_def
        else:
                participant = int(sys.argv[2])
        if len(sys.argv)<2:
                dataname = dataname_def
        else:
                dataname = sys.argv[1]        
else:
        dataname = dataname_def
        participant = participant_def
        unique_trials = unique_trials_def

execfile('validate_data.py')

print 'Fitting Data: ' + dataname

# get data from pickle
with open(pickledir+src, "rb" ) as f:
	trials = pickle.load( f )

trials.task = task

print trials
trials = Simulation.extractPptData(trials,participant,unique_trials)


# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 

results = dict()
for model_obj in [ConjugateJK13,RepresentJK13,CopyTweak,Packer]:# [ConjugateJK13, CopyTweak, Packer]:
	res = Simulation.hillclimber(model_obj, trials, options,results=True,callbackstyle='.')
	X = model_obj.params2dict(model_obj.clipper(res.x))
	results[model_obj.model] = X

        #Simulation.show_final_p(model_obj,trials,res.x, show_data = False)
                

for k,v in results.items():
	print k, v

        

# save final result in pickle
with open(pickledir+dst,'wb') as f:
 	pickle.dump(results, f)



