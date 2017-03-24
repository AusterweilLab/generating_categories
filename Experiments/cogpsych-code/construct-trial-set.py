import sqlite3
import os
import pickle
import pandas as pd

execfile('Imports.py')
from Modules.Classes import Optimize

con = sqlite3.connect('experiments.db')
participants = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()


# create categories mapping
mapping = pd.DataFrame(columns = ['condition', 'categories'])
for i in alphas.columns:
	As = alphas[i].as_matrix().flatten()
	mapping = mapping.append(
		dict(condition = i, categories =[As]), 
		ignore_index = True
	)

# merge categories into generation
generation = pd.merge(generation, participants, on='participant')
generation = pd.merge(generation, mapping, on='condition')

# create trial set object
trials = Optimize.Trialset(stimuli = stimuli)
trials = trials.add_frame(generation)

with open('pickles/all_data_e1_e2.p','wb') as f:
	pickle.dump(trials, f)