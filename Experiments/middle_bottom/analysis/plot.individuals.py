import sqlite3, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
os.chdir(sys.path[0])


exec(open('Imports.py').read())
import Modules.Funcs as funcs

pd.set_option('display.precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()

con.close()

savedir = 'individuals'

f, ax= plt.subplots(1,1, figsize=(1.6, 1.6))
for i, row in info.iterrows():
	pid, condition = int(row.participant), row.condition

	palphas = alphas[condition]
	pbetas = df.stimulus[df.participant == pid]

	funcs.plotclasses(ax, stimuli, palphas, pbetas)
	
	fname = os.path.join(savedir,condition + '-' + str(pid) + '.png')
	f.savefig(fname, bbox_inches='tight', transparent=False)
	plt.cla()
