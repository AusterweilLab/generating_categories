import pickle
import pandas as pd
import numpy as np
import time
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13

# Specify default dataname
dataname_def = 'nosofsky1989'
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


s = 'Invalid data name supplied. Please select one of these options:'
choices = ['pooled','pooled-no1st','nosofsky1986','nosofsky1989']

dataname = funcs.valData(dataname,s,choices)

# Data
if dataname == 'pooled':
        # all data
        src = "pickles/all_data_e1_e2.p"
        dst = "pickles/gs_best_params_all_data_e1_e2.p"
        task = "generate"
elif dataname == 'pooled-no1st':
        # trials 2-4
        src = "pickles/trials_2-4_e1_e2.p"
        dst = "pickles/gs_best_params_trials_2-4_e1_e2.p"
        task = "generate"
elif dataname == 'nosofsky1986':
        # nosofsky data
        src = "pickles/nosofsky1986.p"
        dst = "pickles/gs_best_params_nosofsky1986.p"
        task = "assign"
elif dataname == 'nosofsky1989':
        # nosofsky data
        src = "pickles/nosofsky1989.p"
        dst = "pickles/gs_best_params_nosofsky1989.p"
        task = "assign"
else:        
        raise Exception('Invalid data name specified.')

dst_error = dst[0:-2] + '_error.p'

print 'Grid Searching Data: ' + dataname

# get data from pickle
with open(src, "rb" ) as f:
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

#define the function to parallelise over
def parthis(i,startp,model_obj,trials,options,nparms,):
        if np.mod(i,printcol) != 0:
            print str(i),
            sys.stdout.flush()
        elif i>0:
            print str(i)
            
        inits = startp[i,:]
        res = Simulation.hillclimber(model_obj, trials, options,
                                     inits=inits, results = False,
                                     callbackstyle='none')
        final_parms = res.x
        final_ll = res.fun
        final_aic =  funcs.aic(final_ll,nparms)
        final_results_row = np.array(final_parms + [final_ll] + [final_aic]) #np.append(final_parms,final_ll)
        results_array[i,:] = final_results_row
        return results_array


#Run grid search
results = dict()
for model_obj in [ConjugateJK13,CopyTweak,Packer]:# [ConjugateJK13, CopyTweak, Packer]:
    #Prepare list of grid search start points
    #Create base array
    nparms = len(model_obj.parameter_names)
    steps = 5
    stepsize = float(1)/steps
    startp_base = funcs.ndspace(steps+1,nparms,0,1)
    #Set some defaults
    mindef = -6
    maxdef = 6 #follows uniform distribution if using rvs
    #Adjust the scale of the array so the min and max values of parms aren't included
    adjustrangemin = stepsize
    adjustrangemax = 1-stepsize
    adjustrange = adjustrangemax-adjustrangemin
    startp = startp_base*adjustrange+adjustrangemin


    for pname,prule in model_obj.parameter_rules.items():
        idx = model_obj.parameter_names.index(pname)
        if 'max' in prule:
            max = prule['max']
        else:
            max = maxdef
        startp[:,idx] = startp[:,idx] * max
        
        if 'min' in prule:
            min = prule['min']
        else:
            min = mindef
        startp[:,idx] = startp[:,idx] + min

    nfits = startp.shape[0]
    results_array = np.array(np.zeros([nfits,nparms+2])) #nparms+1 cols, where +2 is the LL and AIC
    results_model = dict()
    print 'Fitting: ' + model_obj.model
    print 'Total starting points: ' + str(nfits)
    printcol = 20
    for i in range(nfits):
        if np.mod(i,printcol) != 0:
            print str(i),
            sys.stdout.flush()
        elif i>0:
            print str(i)
            
        inits = startp[i,:]
        res = Simulation.hillclimber(model_obj, trials, options,
                                     inits=inits, results = False,
                                     callbackstyle='none')
        final_parms = res.x
        final_ll = res.fun
        final_aic =  funcs.aic(final_ll,nparms)
        final_results_row = np.array(final_parms + [final_ll] + [final_aic]) #np.append(final_parms,final_ll)
        results_array[i,:] = final_results_row


    #Get indices sorted to LL
    ind = np.argsort( results_array[:,-2] );
    startp_sorted = startp[ind]
    results_array_sorted = results_array[ind]
    results_best = results_array_sorted[0,:]
    results_model['startparms'] = startp_sorted
    results_model['finalparmsll'] = results_array_sorted
    results_model['bestparmsll'] = results_best
    results[model_obj.model] = results_model
        #X = model_obj.params2dict(model_obj.clipper(res.x))
        #results[model_obj.model] = X
        #startp_dict = model_obj.params2dict(model_obj.clipper(inits))
    print '\nDone fitting ' + model_obj.model + '.\n'
    print 'Final results: '
    X = model_obj.params2dict(model_obj.clipper(results_best[0:-2]))
    for k, v in X.items():
	print '\t' + k + ' = ' + str(v) + ','

    print '\tLogLike = ' + str(results_best[-2])                        
    print '\tAIC = ' + str(results_best[-1])
                
#for k,v in results.items():
#	print k, v

        

# save final result in pickle
with open(dst,'wb') as f:
    #pass 
    pickle.dump(results, f)



