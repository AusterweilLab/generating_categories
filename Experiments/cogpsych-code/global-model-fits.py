import pickle
import pandas as pd

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13

# Specify default dataname
dataname_def = 'nosofsky1986'

#Allow for input arguments at the shell
if __name__ == "__main__":
        import sys
        
        if len(sys.argv)<2:
                dataname = dataname_def
        else:
                dataname = sys.argv[1]        
else:
        dataname = dataname_def
        
s = 'Invalid data name supplied. Please select one of these options:'
choices = ['pooled','pooled-no1st','nosofsky1986','nosofsky1986p0','nosofsky1986p1']        

dataname = funcs.valData(dataname,s,choices)

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
elif dataname == 'nosofsky1986p0':
        # nosofsky data
        src = "pickles/nosofsky1986_p0.p"
        dst = "pickles/best_params_nosofsky1986_p0.p"
        task = "assign"
elif dataname == 'nosofsky1986p1':
        # nosofsky data
        src = "pickles/nosofsky1986_p1.p"
        dst = "pickles/best_params_nosofsky1986_p1.p"
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
for model_obj in [ConjugateJK13,CopyTweak,Packer]:# [ConjugateJK13, CopyTweak, Packer]:
	res = Simulation.hillclimber(model_obj, trials, options)
	X = model_obj.params2dict(model_obj.clipper(res.x))
	results[model_obj.model] = X
        if task is 'assign':
                pass
                #Simulation.show_final_p(model_obj,trials,res.x, show_data = True)
                

for k,v in results.items():
	print k, v

        
lll
# save final result in pickle
with open(dst,'wb') as f:
	pickle.dump(results, f)



