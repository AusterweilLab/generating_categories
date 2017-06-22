import sqlite3, sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


execfile('Imports.py')
import Modules.Funcs as funcs


con = sqlite3.connect('../data/experiment.db')
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
alphas = pd.read_sql_query("SELECT * from alphas", con)
con.close()



f, ax = plt.subplots(1, 2, figsize=(3.3, 1.5))
for i, k  in enumerate(list(alphas)):
	h = ax[i]
	funcs.plotclasses(h, stimuli, alphas[k], [])		

	h.axis(np.array([-1, 1, -1, 1])*1.25)
	# h.text(-1.1, 1.1, k, ha = 'left', va = 'top')
	h.set_title(k)
	[i.set_linewidth(0.5) for i in h.spines.itervalues()]

f.savefig('conditions.pdf', bbox_inches='tight', transparent=True)

path = '../../../Manuscripts/cog-psych/figs/e2-conditions.pgf'
# funcs.save_as_pgf(f, path)