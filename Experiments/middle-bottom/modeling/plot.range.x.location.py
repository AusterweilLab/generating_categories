import sqlite3
import numpy as np
import pandas as pd
import pickle

from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt

# set statistic of interest
STAT_OF_INTEREST = 'drange'
STAT_LIMS =  (-2.0, 2.0)

# prior mu for normal inverse gamma
PRIOR_MU = 0.0
PRIOR_NU = 1.0

# simulation params
N_SAMPLES = 50
WT_THETA = 1.5

# plotting settings
fontsettings = dict(fontsize = 11.0)
col_order = ['Behavioral', 'PACKER', 'Copy and Tweak', 'Hierarchical Sampling']
row_order = ['Middle', 'Bottom']
SMOOTHING_PARAM = 0.8


# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT participant, stimulus from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

nstimuli = stimuli.shape[0]

# get 'observed' dataframe with columns:
# condition, stimulus, mean, size
observed = pd.merge(generation, stats[['participant', STAT_OF_INTEREST]], on='participant')
observed = pd.merge(observed, info[['participant', 'condition']], on='participant')
observed = observed.groupby(['condition','stimulus'])[STAT_OF_INTEREST].agg(['mean', 'size'])
observed = observed.reset_index()

# store all data (models and behavioral alike) here
all_data = dict(Behavioral = observed)

# add modeling module
execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13, Simulation
import Modules.Funcs as funcs

with open('pickles/best_params_all_trials.p','r') as fh:
	best_params = pickle.load( fh )

name_2_object = {
    'PACKER': Packer, 
    'Copy and Tweak': CopyTweak, 
    'Hierarchical Sampling': ConjugateJK13
}

# conduct simulations
for model_name, model_obj in name_2_object.items():
    print 'Running: ' + model_obj.model
    params  = best_params[model_name]

    model_data = pd.DataFrame(columns = ['condition','stimulus',STAT_OF_INTEREST])

    for i, row in stats.groupby('participant'):
        pcond = info.loc[info.participant == i, 'condition'].iloc[0]
        As = stimuli[alphas[pcond],:]

        # get weights
        params['wts'] = funcs.softmax(-row[['xrange','yrange']], theta = WT_THETA)[0]
        if model_obj ==  ConjugateJK13:
            params['wts'] = 1.0 - params['wts']

        # simulate
        model = model_obj([As], params)
        for j in range(N_SAMPLES):   
            nums = model.simulate_generation(stimuli, 1, nexemplars = 4)
            model.forget_category(1)

            # run stats battery
            all_stats = funcs.stats_battery(stimuli[nums,:], As)

            # convert to row for df
            rows = dict(condition = [pcond] *4, stimulus = nums)
            rows[STAT_OF_INTEREST] = [all_stats[STAT_OF_INTEREST]]*4
            model_data = model_data.append(pd.DataFrame(rows), ignore_index = True)

        print '\t' + str(i)

    # aggregate over simulations, add to all data
    model_data = model_data.groupby(['condition','stimulus'])[STAT_OF_INTEREST]
    model_data = model_data.agg(['mean', 'size'])
    model_data = model_data.reset_index()
    model_data['size'] /= float(N_SAMPLES)
    all_data[model_obj.model] = model_data

# plotting
f, ax = plt.subplots(2,4,figsize = (6.4, 2.5))
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
            if lab == 'Hierarchical Sampling':
                lab = 'Hierarchical\nBayesian'
            if lab == 'Copy and Tweak':
                lab = 'Copy &  Tweak'
            h.set_title(lab, **fontsettings)

        if colnum == 0:
            h.set_ylabel(c, **fontsettings)


# add colorbar
cbar = f.add_axes([0.95, 0.1, 0.04, 0.7])
f.colorbar(im, cax=cbar, ticks=[-2, 2], orientation='vertical')
cbar.set_yticklabels([
    'Vertically\nAligned\nCategory', 
    'Horizontally\nAligned\nCategory', 
],**fontsettings)
cbar.tick_params(length = 0)

plt.tight_layout(w_pad=-4.0, h_pad= 0.1)

fname = 'gradients-' + STAT_OF_INTEREST
f.savefig(fname + '.pdf', bbox_inches='tight', transparent=True)
f.savefig(fname + '.png', bbox_inches='tight', transparent=True)

# path = '../../../Manuscripts/cogsci-2017/figs/range-diff-gradients.pgf'
# funcs.save_as_pgf(f, path)
