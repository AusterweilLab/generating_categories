import numpy as np
import pandas as pd
pd.set_option('precision', 3)
np.set_printoptions(precision = 3)

import sqlite3
import pickle
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
# custom modules
execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13, RepresentJK13, CopyTweakRep
import Modules.Funcs as funcs

# set statistic of interest
STAT_OF_INTEREST = 'drange'
STAT_LIMS =  (-2.0, 2.0)

# STAT_OF_INTEREST = 'correlation'
# STAT_LIMS =  (-1.0, 1.0)

# prior mu for normal inverse gamma
PRIOR_MU = 0.0
PRIOR_NU = 1.0

# simulation params
N_SAMPLES = 30
WT_THETA = 1.5

# plotting settings
fontsettings = dict(fontsize = 12.0)
col_order = ['Behavioral', 'PACKER', 'Copy and Tweak','Hierarchical Sampling With Representativeness', 'Hierarchical Sampling']
#col_order = ['Hierarchical Sampling With Representativeness']
col_names_short = ['Behavioral', 'PACKER', 'Copy & Tweak','Representativeness', 'Hier. Bayes']
row_order = ['Corner_S','Corner_C']#['Cluster','Row', 'XOR', 'Bottom', 'Middle']
SMOOTHING_PARAM = 0.8

dbname = 'experiment-corner.db'#'experiments-5con.db'#raw data
dataname = '5con'#'5con'#bestparms comes from here

execfile('validate_data.py') #get path to param pickle

if dbname=='experiments-pooled.db':
    e1e2mark = True #Add plot grouping markers or not?
else:
    e1e2mark = False

# import data
con = sqlite3.connect(dbname)
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

# get 'observed' dataframe with columns:
# condition, stimulus, mean, size
observed = pd.merge(generation, stats[['participant', STAT_OF_INTEREST]], on='participant')
observed = pd.merge(observed, info[['participant', 'condition']], on='participant')
observed = observed.groupby(['condition','stimulus'])[STAT_OF_INTEREST].agg(['mean', 'size'])
observed = observed.reset_index()

# store all data (models and behavioral alike) here
all_data = dict(Behavioral = observed)


# get best params pickle
with open("pickles/chtc_gs_best_params_{}".format(src), "rb" ) as f:
    best_params_t = pickle.load( f )

#Rebuild it into a smaller dict
best_params = dict()
for modelname in best_params_t.keys():    
    best_params[modelname] = dict()
    for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
        parmval = best_params_t[modelname]['bestparmsll']
        best_params[modelname][parmname] = parmval[i]

name_2_object = {
    'PACKER': Packer, 
    'Copy and Tweak': CopyTweak, 
    'Hierarchical Sampling': ConjugateJK13,
    'Hierarchical Sampling With Representativeness': RepresentJK13,
    #'Copy and Tweak Rep': CopyTweakRep
}

# conduct simulations
for model_name, model_obj in name_2_object.items():
    print 'Running: ' + model_obj.model
    params  = best_params[model_name]

    model_data = pd.DataFrame(columns = ['condition','stimulus',STAT_OF_INTEREST])

    for i, row in stats.groupby('participant'):
        pcond = info.loc[info.participant == i, 'condition'].iloc[0]
        As = stimuli[alphas[pcond],:]
        if 'wrap_ax' in generation.columns:
            wrap_ax = generation.loc[generation.participant==i].wrap_ax.values[0]
            if np.isnan(wrap_ax):
                wrap_ax = None
            else:
                wrap_ax = int(wrap_ax)
        else:
            wrap_ax = None

        # get weights
        if 'range' in STAT_OF_INTEREST:
            params['wts'] = funcs.softmax(-row[['xrange','yrange']], theta = WT_THETA)[0]
            if model_obj ==  ConjugateJK13 or model_obj ==  RepresentJK13:
                params['wts'] = 1.0 - params['wts']
        else:
            params['wts'] = np.array([0.5, 0.5])

        # assume no baselinesim
        params['baselinesim'] = 0        
        # simulate
        model = model_obj([As], params,funcs.getrange(stimuli))
        for j in range(N_SAMPLES):   
            nums = model.simulate_generation(stimuli, 1, nexemplars = 4,wrap_ax=wrap_ax)
            model.forget_category(1)

            # run stats battery
            all_stats = funcs.stats_battery(stimuli[nums,:], As,wrap_ax = wrap_ax)

            # convert to row for df
            # handle variable number of generated exemplars
            numgen = len(nums)
            rows = dict(condition = [pcond] *numgen, stimulus = nums)
            rows[STAT_OF_INTEREST] = [all_stats[STAT_OF_INTEREST]]*numgen
            
            model_data = model_data.append(pd.DataFrame(rows), ignore_index = True)

        print '\t' + str(i)
        
    # aggregate over simulations, add to all data
    model_data = model_data.groupby(['condition','stimulus'])[STAT_OF_INTEREST]
    model_data = model_data.agg(['mean', 'size'])
    model_data = model_data.reset_index()
    model_data['size'] /= float(N_SAMPLES)
    all_data[model_obj.model] = model_data

# plotting
f, ax = plt.subplots(len(row_order),len(name_2_object)+1,figsize = (10, 10))
for rownum, c in enumerate(row_order):
    A = stimuli[alphas[c],:]
    
    for colnum, lab, in enumerate(col_order):
        data = all_data[lab]
        h = ax[rownum][colnum]
        df = data.loc[data.condition == c]

        # get x/y pos of examples
        x, y = stimuli[:,0], stimuli[:,1]
    
        # compute color value of each example
        vals = np.zeros(stimuli.shape[0])
        for i, row in df.groupby('stimulus'):
            n = row['size'].as_matrix()
            sumx = row['mean'].as_matrix() * n
            vals[int(i)] = (PRIOR_NU * PRIOR_MU +  sumx) / (PRIOR_NU + n)

        print c, colnum, min(vals), max(vals)

        # smoothing
        g = funcs.gradientroll(vals,'roll')[:,:,0]
        g = gaussian_filter(g, SMOOTHING_PARAM)
        vals = funcs.gradientroll(g,'unroll')
        
        im = funcs.plotgradient(h, g, A, [], clim = STAT_LIMS, cmap = 'PuOr')

        # axis labeling
        if rownum == 0:
            h.set_title(col_names_short[colnum], **fontsettings)

        if colnum == 0:
            h.set_ylabel(c, **fontsettings)

        # experiment 1 and 2 markers
        if e1e2mark:
            if rownum == 1 and colnum == 0:
                h.text(-3.5, np.mean(h.get_ylim()), 'Experiment 1', 
                    ha = 'center', va = 'center', rotation = 90, fontsize = fontsettings['fontsize'] + 1)
                h.plot([-2.7,-2.7],[-9,17],'-', color='gray', linewidth = 1, clip_on=False)

            if rownum == 3 and colnum == 0:
                h.text(-3.5, -0.5, 'Experiment 2', 
                    ha = 'center', va = 'center', rotation = 90, fontsize = fontsettings['fontsize'] + 1)
                h.plot([-2.7,-2.7],[-9,8],'-', color='gray', linewidth = 1, clip_on=False)


# add colorbar
cbar = f.add_axes([0.21, -0.02, 0.55, 0.03])
f.colorbar(im, cax=cbar, ticks=[-2, 2], orientation='horizontal')
cbar.set_xticklabels([
    'Vertically Aligned\nCategory', 
    'Horizontally Aligned\nCategory', 
],**fontsettings)
cbar.tick_params(length = 0)

plt.tight_layout(w_pad=-2.0, h_pad= .5)

fname = 'gradients-t-' + STAT_OF_INTEREST
f.savefig(fname + '.pdf', bbox_inches='tight', transparent=False)
#f.savefig(fname + '.png', bbox_inches='tight', transparent=False)

#path = '../../Manuscripts/cog-psych/revision/figs/range-diff-gradients.pgf'
#funcs.save_as_pgf(f, path)
