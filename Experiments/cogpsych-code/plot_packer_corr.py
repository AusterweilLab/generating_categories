import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import get_corr as gc
import sqlite3
import math
from scipy.stats import stats as ss

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import Packer, CopyTweak
WT_THETA = 1.5

#toggle parallelisation of corr computation
parallelOn = False

# get trials pickle
# pickle can be "pickles/all_data_e1_e2.p", "pickles/nosofsky1986.p"
with open("pickles/all_data_e1_e2.p", "rb" ) as f:
    trials = pickle.load( f )

# get best params pickle
# pickle can be "pickles/best_params_all_data_e1_e2.p", "pickles/best_params_nosofsky1986.p"
# get best params pickle
with open("pickles/chtc_gs_best_params_all_data_e1_e2.p", "rb" ) as f:
    best_params_t = pickle.load( f )

#Rebuild it into a smaller dict
best_params = dict()
for modelname in best_params_t.keys():    
    best_params[modelname] = dict()
    for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
        parmval = best_params_t[modelname]['bestparmsll']
        best_params[modelname][parmname] = parmval[i]

# with open("pickles/best_params_all_data_e1_e2.p", "rb" ) as f:
#     best_params = pickle.load( f )

# compute copytweak loglike
start_params = best_params[CopyTweak.model]
#start_params = best_params[Packer.model]

# add task type to trials object
trials.task = 'generate'

#Get learning data
#data_assign_file = '../cat-assign/data/experiment.db'
data_assign_file = 'experiment-catassign.db'
con = sqlite3.connect(data_assign_file)
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * FROM assignment", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

#Get generation data
data_generate_file = 'experiment-midbot.db'
con = sqlite3.connect(data_generate_file)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

#Get unique ppts
pptlist = []#np.array([]);
for i,row in info.iterrows():
    pptlist += [row.pptmatch]
        #    pptlist = np.concatenate((pptlist,trial['participant']))
pptlist = np.unique(pptlist)

# set up grid of param values
gamma_grid = np.linspace(0, 20.0, 100)
corrs = np.empty(gamma_grid.shape)

# evaluate correlation at each grid point
catassign_corrs = "pickles/catassign_packer_corr20.p"


try:
    with open(catassign_corrs,'rb') as f:
        corrs = pickle.load(f)

except:
    #Generate some key variables (ppt errors, trialset objects)
    pptdata,tso = funcs.prep_corrvar(info,assignment,stimuli,stats,WT_THETA)
    
    if parallelOn:
        #Try parallelising the calculation of corrs
        curr = []
        def gcpar(parm):
            #helper function to make parallelising get_corr easier
            print '.'
            corr = funcs.get_corr(parm,pptdata,tso,Packer,print_on = False, parmxform=True)[0] #-trials.loglike(curr, Packer)
            corr = -corr
            return corr
        for i, val in enumerate(gamma_grid):
            curr_el = start_params.copy()
            curr_el['theta_cntrst'] = val
            curr_el['theta_target'] = curr_el['determinism']
            #curr_el = Packer.parmxform(curr_el, direction = 1)
            curr += [curr_el]        
        from multiprocessing import Pool
        pool = Pool()
        args = curr
        corrs_temp = pool.map(gcpar, args)
        for i in range(len(corrs)):
            corrs[i] = corrs_temp[i]

    else:
        for i, val in enumerate(gamma_grid):
            curr = start_params.copy()
            curr['theta_cntrst'] = val
            curr['theta_target'] = curr['determinism']
            #curr = Packer.parmxform(curr, direction = 1)
            corr = funcs.get_corr(curr,pptdata,tso,Packer,print_on = False, parmxform=True)[0] #-trials.loglike(curr, Packer)
            corrs[i] = -corr
            print corrs[i]
            
    #Save pickle for faster running next time
    with open(catassign_corrs, "wb" ) as f:
        pickle.dump(corrs, f)



for i in range(len(gamma_grid)):
    print i, gamma_grid[i], corrs[i]

# plot it
fh = plt.figure(figsize=(5,3))

# copytweak annotation
copytweak_corrs = corrs[gamma_grid == 0]
plt.plot([min(gamma_grid), max(gamma_grid)], [copytweak_corrs, copytweak_corrs], '--', linewidth = 1, color='gray')
plt.text(12, copytweak_corrs-.06, 'Target Only (Copy & Tweak)', ha = 'center', va = 'bottom')

# contrast only annotation
contrast_corrs = corrs[gamma_grid == 2]
#plt.plot([min(gamma_grid), max(gamma_grid)], [contrast_corrs, contrast_corrs], '--', linewidth = 1, color='gray')
#plt.text(0.5, contrast_corrs, 'Contrast Only', ha = 'center', va = 'bottom')

# PACKER annotation
x = float(gamma_grid[corrs == max(corrs)])
plt.text(x, max(corrs), 'PACKER', ha = 'center', va = 'bottom', fontsize = 12)


# plot main line
plt.plot(gamma_grid, corrs,'k-', linewidth = 1)
plt.xlabel(r'$\theta_c$ Parameter Value', fontsize = 12)

xstep = 10
xticks = np.round(np.arange(min(gamma_grid),max(gamma_grid)+xstep,xstep),1)
xticklabels = [str(i) for i in xticks]
xticklabels[0] = '0'
#xticklabels[-1] = '1'
plt.xticks(xticks)
#fh.gca().set_xticklabels(xticklabels)

yticks = np.arange(0,1,.2)
yticklabels = [str(round(i,1)) for i in yticks]
plt.yticks(yticks)
fh.gca().set_yticklabels(yticklabels)

plt.gca().yaxis.grid(True)
plt.ylabel('Correlation ($r$)', fontsize = 12)

plt.savefig('packer-corr.pdf', bbox_inches='tight', transparent=False)
#path = '../../Manuscripts/cog-psych/revision/figs/packer-corrs.pgf'
#funcs.save_as_pgf(fh, path)
