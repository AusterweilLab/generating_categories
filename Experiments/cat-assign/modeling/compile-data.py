# compile the data into a useful format for modeling

import pandas as pd
import sqlite3
import pickle

execfile('Imports.py')
from Modules.Classes import Simulation

pd.set_option('display.width', 200, 'precision', 2)


dbpath = '../data/experiment.db'                           

# KEEP:
keep_tables = [
    'stimuli',          # one copy
    'alphas',           # add columns
    'participants',     # add rows; INCREMENET PID; ADD EXPERIMENT MARKER
    'betastats',        # add rows; INCREMENET PID
    'generation',       # add rows; INCREMENET PID
]

# grab data
with sqlite3.connect(dbpath) as con:
    participants = pd.read_sql_query("SELECT * from participants", con)
    generation = pd.read_sql_query("SELECT * from generation", con)
    alphas = pd.read_sql_query("SELECT * from alphas", con)
    stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()

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
trials = Simulation.Trialset(stimuli)
trials = trials.add_frame(generation)


with open('pickles/all_trials.p','wb') as f:
    pickle.dump(trials, f)

# weed out first trials
trials.Set = [i for i in trials.Set if len(i['categories'][1])>0]
trials._update()

with open('pickles/trials_2-4.p','wb') as f:
    pickle.dump(trials, f)
