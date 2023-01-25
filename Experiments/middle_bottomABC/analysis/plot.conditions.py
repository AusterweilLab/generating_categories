import sqlite3, sys, os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

os.chdir(sys.path[0])

exec(open('Imports.py').read())
import Modules.Funcs as funcs


con = sqlite3.connect('../data/experiment.db')
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()
alphas = pd.read_sql_query("SELECT * from alphas", con)
con.close()

f, ax = plt.subplots(1, 2, figsize=(3.3, 1.5))
# f, ax = plt.subplots(2, 1, figsize=(1.5, 3.3))

for i, k  in enumerate(list(alphas)):
	h = ax[i]
	funcs.plotclasses(h, stimuli, alphas[k], [])		

	h.axis(np.array([-1, 1, -1, 1])*1.25)
	h.text(-1.1, 1.1, k, ha = 'left', va = 'top')
	
	# h.plot([-1,1],[-0.9,-0.9],'--',color='gray')
	# h.plot([-1,1],[0.9,0.9],'--',color='gray')
	# h.text(0.0,0.9,'Top',ha = 'center',va = 'bottom', color='gray')
	# h.text(0.0,-0.9,'Bottom',ha = 'center',va = 'top', color='gray')
	[i.set_linewidth(0.5) for i in iter(h.spines.values())]

f.savefig('conditions.pdf', bbox_inches='tight', transparent=True)
f.savefig('conditions.png', bbox_inches='tight', transparent=True)

# path = '../../../Manuscripts/cog-psych/figs/e2-conditions.pgf'
# funcs.save_as_pgf(f, path)