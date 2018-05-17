#Take out the individual fits and do stuff with them (plots etc)
import pickle, math
import pandas as pd
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
import pandas as pd

# Specify default dataname
dataname_def = 'midbot'#'nosofsky1986'#'NGPMG1994'
participant_def = 'all'
unique_trials_def = 'all'
dataname = dataname_def
execfile('validate_data.py')
# get data from pickle
with open(pickledir+src,"rb" ) as f:
    trials = pickle.load( f )

# get best params pickle
#bestpickle = "pickles/private/chtc_ind_gs_best_params_all_data_e1_e2.p"
bestpickle = "pickles/private/chtc_ind_gs_best_params_catassign.p"
with open(bestpickle, "rb" ) as f:
    results_t = pickle.load( f )

#Rebuild results into dataframe
best_params = dict()
results = dict()
for modelname in results_t.keys():    
    results[modelname] = pd.DataFrame()
    ppts = results_t[modelname].keys()
    for ppt in ppts:
        tempdict = dict()
        if ppt==0:
            parmnames = results_t[modelname][ppt]['parmnames']
        for i,parmname in enumerate(parmnames):            
            parmval = results_t[modelname][ppt]['bestparmsll']
            tempdict[parmname] = parmval[i]
            # best_params[modelname][ppt][parmname] = parmval[i]
        tempdict['nLL'] = parmval[i+1]
        tempdict['AIC'] = parmval[i+2]
        results[modelname] = results[modelname].append(tempdict, ignore_index = True)

#Plot!
fh,axs = plt.subplots(1,len(results.keys()),figsize=(20,7))
for m,model in enumerate(results.keys()):
    #x = np.histogram(results[model]['nLL'])
    #plt.bar(x[1][0:-1],x[0],width=1)
    axs[m].hist(results[model]['nLL'],linewidth=1,edgecolor='black')
    axs[m].set_title(model)
    axs[m].set_xlabel('negLL')
    if m==0:
        axs[m].set_ylabel('Frequency')
    axs[m].set_ylim([0,40])
    
plt.show()
        
#modelList = [Packer,CopyTweak,ConjugateJK13,RepresentJK13]                            
