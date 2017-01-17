import sqlite3, os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "../../../Modules/")
import utils

pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()

con.close()

savedir = 'individuals'

f, ax= plt.subplots(1,1, figsize=(2, 2))
for i, row in info.iterrows():
	pid, condition = int(row.participant), row.condition

	palphas = alphas[condition]
	pbetas = df.stimulus[df.participant == pid]

	utils.plotclasses(ax, stimuli, palphas, pbetas)
	
	fname = os.path.join(savedir,condition + '-' + str(pid) + '.png')
	f.savefig(fname, bbox_inches='tight', transparent=False)
	plt.cla()
