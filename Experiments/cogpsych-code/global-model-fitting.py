import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Optimize

pd.set_option('display.width', 200, 'precision', 2)

con = sqlite3.connect('experiments.db')
participants = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

# make indexing a little cleaner...
participants.set_index('participant', inplace = True)

trials = Optimize.Trialset(stimuli = stimuli)
for pid, rows in generation.groupby('participant'):
	As = alphas[participants.loc[pid, 'condition']].as_matrix()

	for num, row in rows.groupby('trial'):
		Bs = rows.loc[rows.trial<num, 'stimulus'].as_matrix()
		stimulus = int(row.stimulus)
		trials.add(stimulus, categories = [As, Bs], 
			trial = num, participant = pid)



for i in trials.compactset:
	print i

