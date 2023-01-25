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
dataname = 'pooled'
execfile('validate_data.py')
with open(pickledir+src,'rb') as f:
    trials = pickle.load(f)
trials.task = task

with open(pickledir+'/corrvar.p','rb') as f:
    corrvar = pickle.load(f)
tso = corrvar['tso']
pptdata = corrvar['pptdata']  

def easymodel(model,params,trialnum):
    # format categories
    trial = trials.Set[trialnum]
    #categories = [trials.stimuli[i,:] for i in trial['categories'] if any(i)]
    categories = [trials.stimuli[i,:] for i in trial['categories'] if len(i)>0]
    #Returns generated ps 
    ps = model(categories, params, trials.stimrange).get_generation_ps(trials.stimuli, 1, trials.task)
    return ps

#temp model runs
packerparms = [.506, 3.08,3.47]#[.302,2.533,6.004]#[.263,.321,9.479]
#packerparms2 = [.5,.7,.3]#[.302,6.004,2.533]#[.263,.321,9.479]
#copytweakparms = [.217796,.01]#[.263, 9.807]
hbparms = [12.226, 1, 27.041,10.214]

#getcorr
#corr = funcs.get_corr(CopyTweak.parmxform(copytweakparms,direction=1),pptdata,tso,CopyTweak,return_ll=False)
#ll = funcs.get_corr(CopyTweak.parmxform(copytweakparms,direction=1),pptdata,tso,CopyTweak,return_ll=True)
#print corr
#print ll

#print easymodel(ConjugateJK13,hbparms,0)
#print easymodel(RepresentJK13,hbparms,0)

f, ax = plt.subplots(1,2)
ao = easymodel(RepresentJK13,hbparms,20)
a = np.flipud(ao.reshape([9,9]))
bo = easymodel(Packer,packerparms,20)
b = np.flipud(bo.reshape([9,9]))
ax[0].imshow(a,cmap='hot',interpolation='nearest')
ax[1].imshow(b,cmap='hot',interpolation='nearest')
print ao
plt.show()

#packerparms2 = [copytweakparms[0], 0, copytweakparms[1]]
#print trials.loglike(packerparms,PackerRep,parmxform=False)
#print trials.loglike(copytweakparms,CopyTweak,parmxform=False)

#test_cp = easymodel(CopyTweak,copytweakparms,19)
#test_packer = easymodel(PackerRep,packerparms2,19)


#print test_packer
#print test_cp-test_packer
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
