#Temporary file to generate ps plots
#Gives a good idea of the distribution of generation probabilities at each step of exemplar generation
#given some parameter and alpha stimuli values
import pickle, math
import pandas as pd
import sys, os
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
from scipy.stats.stats import pearsonr
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
#Close figures
plt.close()

#load data
dataname_def = 'catassign'#'nosofsky1986'#'NGPMG1994'
participant_def = 'all' #cluster: 0,6,15; XOR: 10; row: 1,11; bottom: 208
unique_trials_def = 'all'
dataname = dataname_def
ind = True #individual fits or not?

narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    participant = int(sys.argv[1])
else:
    participant = participant_def

execfile('validate_data.py')

# get data from pickle
with open(pickledir+src, "rb" ) as f:
    trials = pickle.load( f )
trials.task = task

if task is 'generate':
    print "The task has to be 'assign' or 'error' for this to work."
    exit()

trials = Simulation.extractPptData(trials,participant,unique_trials_def)


#paramsT = dict(params)
models = [Packer,CopyTweak,ConjugateJK13,RepresentJK13]
#paramsP = dict(determinism = 2,specificity=.5,tradeoff=.5,wts=[.5,.5])
#paramsCT = dict(paramsP)
#paramsCT.pop('tradeoff')
ppt = 0
maxppt = 122
while ppt<122:    
    pptTrialObj = Simulation.extractPptData(trials,ppt,unique_trials_def)    
    for trial in pptTrialObj.Set:
        error = 0
        numresp = 0
        for cat in range(len(trial['categories'])):            
            catmembers = trial['categories'][cat]
            response = trial['response'][cat]
            numresp += len(response)
            checklist = np.zeros(len(response),dtype='bool')
            for checkmember in catmembers:
                checklist += response == checkmember
            error += sum(1-checklist)
        error_rate = error/float(numresp)
        print 'Participant {} error: {}'.format(ppt,str(round(error_rate,2)))
    ppt += 1
