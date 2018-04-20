#Temporary file to generate ps plots
#Gives a good idea of the distribution of generation probabilities at each step of exemplar generation
#given some parameter and alpha stimuli values
import pickle, math
import pandas as pd
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from scipy.stats.stats import pearsonr
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
#Close figures
plt.close()

#load data
dataname_def = 'pooled'#'nosofsky1986'#'NGPMG1994'
participant_def = 204 #'all'
unique_trials_def = 'all'
dataname = dataname_def
execfile('validate_data.py')

# get data from pickle
with open(pickledir+src, "rb" ) as f:
    trials = pickle.load( f )
trials.task = task

pptTrialObj = Simulation.extractPptData(trials,participant_def,unique_trials_def)
#Get best parms
with open(pickledir+'gs_'+dst, "rb" ) as f:
    best_params_t = pickle.load( f )
#Rebuild it into a smaller dict
best_params = dict()
for modelname in best_params_t.keys():    
    best_params[modelname] = dict()
    for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
        parmval = best_params_t[modelname]['bestparmsll']
        best_params[modelname][parmname] = parmval[i]

#paramsT = dict(params)
models = [Packer,CopyTweak,ConjugateJK13]
#paramsP = dict(determinism = 2,specificity=.5,tradeoff=.5,wts=[.5,.5])
#paramsCT = dict(paramsP)
#paramsCT.pop('tradeoff')

paramsP = best_params[Packer.model]
paramsP['baselinesim'] = 0
#paramsP['wts'] = paramsT['wts']
paramsCT = best_params[CopyTweak.model]
paramsCT['baselinesim'] = 0
#paramsCT['wts'] = paramsT['wts']
paramsJK = best_params[ConjugateJK13.model]
paramSet = [paramsP,paramsCT,paramsJK]
STAT_LIMS =  (-1.0, 1.0)

ntrials = len(pptTrialObj.Set)
plt.ioff()
plt.ion()
f,ax = plt.subplots(ntrials,len(models),figsize = (6.7, 7.5))

#Sort trial obj by trial number
trialList = []
for t,trialobj in enumerate(pptTrialObj.Set):
    nbeta = len(trialobj['categories'][1])
    pptTrialObj.Set[t]['trial'] = nbeta

for trial in range(ntrials):
    objIdx=0 #find the right trial in the trial obj
    for obj in pptTrialObj.Set:
        if obj['trial']==trial:
            break
        objIdx += 1
    plotct = 0    
    categories = [pptTrialObj.stimuli[i,:] for i in pptTrialObj.Set[objIdx]['categories'] if len(i)>0]

    A = categories[0]
    resp = pptTrialObj.stimuli[pptTrialObj.Set[objIdx]['response'],:]
    if len(categories)>1:
        #include the response
        B = np.append(categories[1],resp,axis=0)
    else:
        B = resp

    ps = []
    for i,model in enumerate(models):
        params = paramSet[i]
        #reverse-transform
        #params = model.parmxform(params, direction = -1)
        ps += [model(categories,params).get_generation_ps(pptTrialObj.stimuli,1,'generate')]
        
    plotVals = []
    psMax = 0
    psMin = 1
    #Get range
    for ps_el in ps:
        psMax = max(psMax,ps_el.max())
        psMin = min(psMin,ps_el.min())

    #Normalise all values
    psRange = psMax-psMin
    for i,ps_el in enumerate(ps):
        plotct += 1
        gps = funcs.gradientroll(ps_el,'roll')[:,:,0]
        plotVals += [(gps-psMin)/psRange]
        #ax = f.add_subplot(trials,2,plotct)
        #print B
        im = funcs.plotgradient(ax[trial,i], plotVals[i], A, B, clim = STAT_LIMS, cmap = 'PuOr')
        ax[trial,i].set_ylabel('Trial {}'.format(trial))
        # cbar = f.add_axes([0.21, .1, 0.55, 0.12])
        # f.colorbar(im, cax=cbar, ticks=[0, 1], orientation='horizontal')

    #Print probabilities up to trial num
    nll = np.zeros(len(models))
    for m,model in enumerate(models):
        params = paramSet[m]
        #params = model.parmxform(params, direction = -1)                        
        for t in range(trial+1):    
            categoriesT = [pptTrialObj.stimuli[i,:] for i in pptTrialObj.Set[t]['categories'] if any(i)]    
            psT = model(categoriesT,params).get_generation_ps(pptTrialObj.stimuli,1,'generate')
            psT_raw = psT[pptTrialObj.Set[t]['response']]
            nll[m] += -np.log(psT_raw)
    #print nll

#plt.tight_layout(w_pad=-4.0, h_pad= 0.5)
plt.draw()
plt.ioff()
