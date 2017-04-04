import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

execfile('Imports.py')
import Modules.Funcs as funcs
from JK13 import JK13

# import data
con = sqlite3.connect('experiment.db')
distances = pd.read_sql_query("SELECT * from distances", con)
training = pd.read_sql_query("SELECT * from training", con)
generation = pd.read_sql_query("SELECT * from generation", con)
con.close()

# get all pairwise distances
all_pairs = dict( (i,np.array([])) for i in JK13.conditions)

for (i, c), rows in generation.groupby(['participant','condition']):
	Bs = JK13.getfeatures(rows)
	idx = (training.participant == i) & (training.condition == c)
	As = JK13.getfeatures(training.loc[idx])
	all_pairs[c] = np.append(all_pairs[c],funcs.pdist(As,Bs).flatten())

fh, ax = plt.subplots(1,2,figsize = (6,2.7))



h = ax[0]
x = np.linspace(0, 1, 20)

for i, (k, v) in enumerate(all_pairs.items()):
	y = funcs.histvec(v, x, density = True)
	h.plot(x, y, alpha = 0.7, label = k)

h.xaxis.grid(False)
h.set_xticks([])
# h.legend(loc = 'upper left', frameon = True, framealpha = 1, fontsize = 10)

# xax = h.axis()
# h.text(xax[0],xax[2] -1, 'Min', fontsize = 10, va = 'top')
# h.text(xax[1],xax[2] -1, 'Max', fontsize = 10, va = 'top', ha = 'right')
# h.set_xlabel('Distance',fontsize = 12)
# h.set_yticks(np.arange(0,35, 5))
# h.set_yticklabels(np.arange(0,35, 5),fontsize = 10)
# h.set_ylabel('Generations Per Stimulus', fontsize = 12)


h = ax[1]
h.plot([0,1],[0,1], '--', color = 'gray', linewidth = 0.5)

for c, rows in distances.groupby('condition'):
	h.plot(rows.Within, rows.Between,	'o', alpha = 0.5, label = c)

h.grid(False)


h.set_xticks([])
h.set_yticks([])

h.axis([0, 1., 0, 1.])
h.legend(loc = 'upper right', frameon = True, framealpha = 1, 
	ncol = 1, columnspacing = 0.1, labelspacing = 0.1, fontsize = 12)
h.set_xlabel('Within-Class Distance',fontsize = 12)
h.set_ylabel('Between-Class Distance',fontsize = 12)


fh.subplots_adjust(wspace=0.3)


fname = 'distance.figs'
fh.savefig(fname + '.png', bbox_inches = 'tight', pad_inches=0.0)

# path = '../../../Manuscripts/cog-psych/figs/e2-distanceplots.pgf'
# funcs.save_as_pgf(fh, path)

		