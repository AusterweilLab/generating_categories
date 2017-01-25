import sqlite3, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

con = sqlite3.connect('../data/experiment.db')
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
alphas = pd.read_sql_query("SELECT * from alphas", con)
con.close()

f, ax = plt.subplots(1, 2, figsize=(3.5, 1.75))
for i, k  in enumerate(list(alphas)):
	h = ax[i]
	utils.plotclasses(h, stimuli, alphas[k], [])		
	h.set_title(k)
	h.axis([-1.2, 1.2, -1.2, 1.2])
	[i.set_linewidth(0.75) for i in h.spines.itervalues()]

f.savefig('conditions.png', bbox_inches='tight', transparent=False)

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
f.savefig('../../../Manuscripts/cogsci-2017/figs/middle-bottom-conditions.pgf',
	bbox_inches='tight', transparent=False,  pad_inches=0.0)