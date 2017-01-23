import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
from models import CopyTweak, Packer, ConjugateJK13
import utils

pd.set_option('precision', 3)
np.set_printoptions(precision = 3)

# get alphas
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()
stats = pd.merge(stats, info, on = 'participant')


models = [
    [CopyTweak, dict(
        specificity = 9.4486327043,
        within_pref = 17.0316650379,
        tolerance = 0.403108523886,
        determinism = 7.07038770338,
        )],
    [Packer, dict(
        specificity = 0.564256174526,
        between = -5.56381151423,
        within = 4.90629512837,
        determinism = 0.63365240101,
        )],
    [ConjugateJK13, dict(
        category_mean_bias = 0.0167065365661,
        category_variance_bias = 1.00003245067,
        domain_variance_bias = 0.163495499745,
        determinism = 2.10276377982,
        )],
]

N = 61
fontopts = dict(fontsize = 11)

def scatterplt(h, x, y, condition):
    styles = dict(Middle = 'ro', Bottom = 'bo')
    h.plot(x, y, styles[condition], alpha = 0.5, label = condition,
        markeredgecolor = 'none'
        )


def format_plot(h, label):
    h.grid(False)
    h.axis([0., 1.5, 0., 1.5])
    h.text(0.05, 1.45, label, ha='left', va = 'top', fontsize = 10)
    h.set_ylabel('')
    h.set_xlabel('')
    h.set_xticks([])
    h.set_yticks([])


# plot between and within scatter
fh, ax = plt.subplots(2,2, figsize = (3.5,3.5))
ax = ax.flat

ax[0].plot([0, 2],[0,2], '--', color = 'gray', linewidth = 0.5)
for c, rows in stats.groupby('condition'):
    scatterplt(ax[0], rows['within'], rows['between'], c)
format_plot(ax[0], 'Behavioral')


for i, (model_obj, params) in enumerate(models):
    h = ax[i+1]
    h.plot([0, 2],[0,2], '--', color = 'gray', linewidth = 0.5)

    for c in alphas.columns.values:
        As = stimuli[alphas[c],:]
        stats = pd.DataFrame(index = range(N), columns = ['within', 'between'])
        
        for j in range(N):
            M = model_obj([As], params)
            betas = M.simulate_generation(stimuli, 1, nexemplars = 4)
            Bs = stimuli[betas,:]
            within = utils.pdist(Bs, Bs)
            within = np.mean(within[np.triu(within)>0])
            between = np.mean(utils.pdist(As, Bs))
            stats.loc[j,:] = dict(within = within, between = between)

        scatterplt(h, stats['within'], stats['between'], c)

    format_plot(h, model_obj.model)
    if i == 1:
        h.text(-0.2, 1.7, 'Between Category Distance', 
            ha = 'center', va = 'center', rotation = 'vertical')
h.legend(frameon = True, bbox_to_anchor = (0.75,-0.3), ncol = 2)
h.text(-0.2, -0.2, 'Within Category Distance', ha = 'center', va = 'center')


fh.savefig('between.within.png', bbox_inches = 'tight')
    
