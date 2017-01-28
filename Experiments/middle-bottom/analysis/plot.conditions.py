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

f, ax = plt.subplots(1, 2, figsize=(3.5, 1.75))
for i, k  in enumerate(list(alphas)):
	h = ax[i]
	funcs.plotclasses(h, stimuli, alphas[k], [])		
	h.set_title(k)
	h.axis([-1.2, 1.2, -1.2, 1.2])
	[i.set_linewidth(0.75) for i in h.spines.itervalues()]

f.savefig('conditions.png', bbox_inches='tight', transparent=False)

path = '../../../Manuscripts/cogsci-2017/figs/middle-bottom-conditions.pgf'
# funcs.save_as_pgf(f, path)