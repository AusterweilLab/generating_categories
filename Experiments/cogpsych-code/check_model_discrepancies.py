#Sometimes when trying to optimize various bits of code, the author may
#inadvertently change the models themselves (because the author is sometimes a
#goob). This script checks the current predictions (well, the loglikelihood of
#best fits) with some gold standard of predictions to see if there is any
#discrepancy.

import pickle
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
from Modules.Classes import CopyTweakRep
from Modules.Classes import PackerRep

saveGold = True

goldfile = 'pickles/goldstate.p'

dataname = 'pooled-no1st'

execfile('validate_data.py')
#Hey, it might be worth implementing validate_data as a function?

with open(pickledir+src,'rb') as f:
    trials = pickle.load(f)
trials.task = task

#Get current best parms
with open(pickledir+bestparmchtc,'rb') as f:
    best_params_t = pickle.load(f)
best_params = funcs.compress_chtc_parms(best_params_t)

modelList = [Packer,CopyTweak,ConjugateJK13,RepresentJK13]
ll = dict()
if saveGold:
    #Save current state as gold standard
    #First, generate loglikelihoods
    for model in modelList:
        ll[model.model] =  trials.loglike(best_params[model.model],model,parmxform=False,seedrng=True)
    with open(goldfile,'wb') as f:
        pickle.dump(ll,f)
        
#Load gold state and compare
with open(goldfile,'rb') as f:
    ll_gold = pickle.load(f)
    
#Get current state
#First, generate loglikelihoods
error = dict.fromkeys(ll_gold.keys(),[])
ll_current = dict()
print 'Gold State match:'
for model in modelList:
    ll_current[model.model] =  trials.loglike(best_params[model.model],model,parmxform=False,seedrng=True)
    error[model.model] = ll_gold[model.model] - ll_current[model.model]
    isequal = ll_current[model.model] == ll_gold[model.model]
    if isequal:
        matchStr = 'Match!'
    else:
        matchStr = 'No match.'
    #Print results
    print '{}: {} Err={}'.format(model.modelshort, matchStr, error[model.model])
