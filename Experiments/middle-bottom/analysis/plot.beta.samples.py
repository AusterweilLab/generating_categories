import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

samples = dict(
	Middle = [
		1, # 4 corner
		7, # bottom row
		68, # side column / corners
		151, # bottom cluster
	],
	Bottom = [
		11, # 4 corner
		91, # top row / corners
		106, # side column
		117, # top cluster
	]
)

fh, ax = plt.subplots(2,4, figsize = [3.2, 1.6])
ax = ax.flat
plotnum = 0
for k, v in samples.items():
	for pid in v:
		h = ax[plotnum]

		A = alphas[k]
		B = generation.loc[generation.participant == pid, 'stimulus']
		utils.plotclasses(h, stimuli, A, B, textsettings = dict(fontsize = 9))
		plotnum += 1
		

plt.tight_layout(pad=-0.0, w_pad=-0.0)
fh.savefig('beta.samples.png', bbox_inches = 'tight')

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
fh.savefig('../../../Manuscripts/cogsci-2017/figs/beta.samples.pgf', bbox_inches='tight', pad_inches=0.0)
