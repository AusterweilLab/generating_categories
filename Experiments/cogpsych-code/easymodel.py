#Script to easily test model predictions

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

#Generate default trialset
dataname = 'pooled-no1st'
execfile('validate_data.py')
with open(pickledir+src,'rb') as f:
    trials = pickle.load(f)
trials.task = task

        

def easymodel(model,params,trialnum):
    # format categories
    trial = trials.Set[trialnum]
    #categories = [trials.stimuli[i,:] for i in trial['categories'] if any(i)]
    categories = [trials.stimuli[i,:] for i in trial['categories'] if len(i)>0]
    #Returns generated ps 
    ps = model(categories, params, trials.stimrange).get_generation_ps(trials.stimuli, 1, trials.task)
    return ps

#temp model runs
packerparms = [.5, 1.0,.0]#[.302,2.533,6.004]#[.263,.321,9.479]
packerparms2 = [.5,.7,.3]#[.302,6.004,2.533]#[.263,.321,9.479]
copytweakparms = [.263, 9.807]
#packerparms2 = [copytweakparms[0], 0, copytweakparms[1]]
print trials.loglike(packerparms,PackerRep,parmxform=False)
#print trials.loglike(copytweakparms,CopyTweakRep,parmxform=False)

test_cp = easymodel(PackerRep,packerparms,19)
test_packer = easymodel(PackerRep,packerparms2,19)


print test_cp
print test_packer
print test_cp-test_packer
lll

#loop over each trial
# for i in range(len(trials.Set)):
#     #These two should return the exact same result
#     test_cp = easymodel(CopyTweakRep,copytweakparms,i)
#     test_packer = easymodel(PackerRep,packerparms2,i)
#     diff = sum(test_cp-test_packer)
#     if diff>0:
#         print i
#         print test_cp
#         print test_packer


#print test_cp-test_packer 
