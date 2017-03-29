import numpy as np
import pandas as pd
pd.set_option('precision', 3)
np.set_printoptions(precision = 3)

import sqlite3
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt

# set statistic of interest
STAT_OF_INTEREST = 'drange'
STAT_LIMS =  (-2.0, 2.0)

# STAT_OF_INTEREST = 'correlation'
# STAT_LIMS =  (-1.0, 1.0)

# prior mu for empirical bayes
PRIOR_MU = 0.0

# simulation params
N_SAMPLES = 20
WT_THETA = 1.5

# plotting settings
fontsettings = dict(fontsize = 10.0)
col_order = ['Behavioral', 'PACKER', 'Copy and Tweak', 'Hierarchical Sampling']
row_order = ['Cluster','Row', 'XOR', 'Bottom', 'Middle']
SMOOTHING_PARAM = 0.8


# import data
con = sqlite3.connect('experiments.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT participant, stimulus from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

# get 'observed' dataframe with columns:
# condition, stimulus, mean, var, size
observed = pd.merge(generation, stats[['participant', STAT_OF_INTEREST]], on='participant')
observed = pd.merge(observed, info[['participant', 'condition']], on='participant')
observed = observed.groupby(['condition','stimulus'])[STAT_OF_INTEREST].agg(['mean', 'var', 'size'])
observed = observed.reset_index()
observed.loc[pd.isnull(observed['var']),'var'] = 1.0

# store all data (models and behavioral alike) here
all_data = dict(Behavioral = observed)

# custom modules
execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13
import Modules.Funcs as funcs

# these values copied from the Slack message sent to Joe
# jk13 values were clipped into allowable range
model_param_pairs = [ 
    [CopyTweak, dict(
    specificity = 3.18895961945,
    determinism = 2.96847856016,
        )],
    [Packer, dict(
    specificity = 0.481287831406,
    between = -0.945026920024,
    within = 1.0440682555,
    determinism = 3.35432164741,
        )],
    [ConjugateJK13, dict(
    category_mean_bias = 1e-10,
    category_variance_bias = 1.0 + 1e-10,
    domain_variance_bias = 5.3127886986,
    determinism = 7.94942567558,
        )],
]


# conduct simulations
for model_obj, params in model_param_pairs:
    print 'Running: ' + model_obj.model
    model_data = pd.DataFrame(columns = ['condition','stimulus',STAT_OF_INTEREST])

    for i, row in stats.groupby('participant'):
        pcond = info.loc[info.participant == i, 'condition'].iloc[0]
        As = stimuli[alphas[pcond],:]

        # get weights
        if 'range' in STAT_OF_INTEREST:
            params['wts'] = funcs.softmax(row[['xrange','yrange']], theta = WT_THETA)[0]
        else:
            params['wts'] = np.array([0.5, 0.5])

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
    model_data = model_data.agg(['mean', 'var', 'size'])
    model_data = model_data.reset_index()
    model_data.loc[pd.isnull(model_data['var']),'var'] = 1.0
    model_data['size'] /= float(N_SAMPLES)
    all_data[model_obj.model] = model_data


# plotting
f, ax = plt.subplots(5,4,figsize = (7.0, 8.5))
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
            sig = row['var'].as_matrix()
            if sig == 0: sig = 0.001
            vals[int(i)] = (PRIOR_MU/sig +  sumx / sig) / (1.0/sig + n/sig)

        print c, colnum, min(vals), max(vals)

        # smoothing
        g = funcs.gradientroll(vals,'roll')[:,:,0]
        g = gaussian_filter(g, SMOOTHING_PARAM)
        vals = funcs.gradientroll(g,'unroll')
        
        im = funcs.plotgradient(h, g, A, [], clim = STAT_LIMS, cmap = 'PuOr')

        # axis labelling
        if rownum == 0:
            h.set_title(lab, **fontsettings)

        if colnum == 0:
            h.set_ylabel(c, **fontsettings)



# add colorbar
# cbar = f.add_axes([0.915, 0.2, 0.03, 0.55])
# f.colorbar(im, cax=cbar, ticks=[-2, 2], orientation='vertical')
# cbar.set_yticklabels([
#     'Vertically\nAligned\nCategory', 
#     'Horizontally\nAligned\nCategory', 
# ],**fontsettings)
# cbar.tick_params(length = 0)

# plt.tight_layout(w_pad=-8.5, h_pad= 0.1)

fname = 'gradients-' + STAT_OF_INTEREST
f.savefig(fname + '.pdf', bbox_inches='tight', transparent=False)
f.savefig(fname + '.png', bbox_inches='tight', transparent=False)

# path = '../../../Manuscripts/cogsci-2017/figs/range-diff-gradient.pgf'
# funcs.save_as_pgf(f, path)