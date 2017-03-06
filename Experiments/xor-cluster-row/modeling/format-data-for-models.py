import sqlite3, pickle
import pandas as pd

# get behavioral data
con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

# set index to make life easier
participants = participants.set_index('participant')

# create list of all trials to simulate
trials = []
for pid, rows in generation.groupby('participant'):
	
	condition = participants.loc[pid, 'condition']
	A =  stimuli[alphas[condition]]
	
	for t in range(4):
		assigned = list( rows.loc[rows.trial <  t, 'stimulus'] )
		response = int(  rows.loc[rows.trial == t, 'stimulus'] )
		
		if not any(assigned): 
			categories = [A] 
		else: 
			B = stimuli[assigned,:]
			categories = [A, B] 

		trials.append(dict(
			participant = pid,
			trial = t,
			categories = categories,
			response = response
		))

print trials

# save to pickle
with open('data.pickle','wb') as f:
	pickle.dump([trials, stimuli], f)


