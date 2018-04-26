# compile the data from the xor-cluster-row and middle-bottom experiments; put it in a
# format that is convenient for simulations

import pandas as pd
import sqlite3
import numpy as np
import pickle

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation

pd.set_option('display.width', 200, 'precision', 2)


databases = [ '../cat-assign/data/experiment.db',
                        ]

# KEEP:
keep_tables = [
    'stimuli',          # one copy
    #'alphas',           # add columns
    'participants', # add rows; INCREMENET PID; ADD EXPERIMENT MARKER
    #'betastats',        # add rows; INCREMENET PID
    'assignment',
    #'generation',       # add rows; INCREMENET PID
]

experiments = pd.DataFrame(columns = ['condition', 'experiment'], dtype = int)

max_known_pid = 0
for num, dbpath in enumerate(databases):

    with sqlite3.connect(dbpath) as con:
        data = dict((T, pd.read_sql('SELECT * FROM ' + T, con)) for T in keep_tables)


    # get the stimuli df, init the alphas
    if num == 0: 
        stimuli = data['stimuli']
        #alphas  = data['alphas']

    # add alpha columns otherwise
    else:
        pass
        #alphas = pd.concat([alphas, data['alphas']], axis=1)

    # update condition mapping
    #rows = [ dict(condition=i, experiment=num) for i in data['alphas'].columns ]
    #experiments = experiments.append(rows, ignore_index = True)

    # remap participant IDs
    data['participants']['original_pid'] = data['participants'].participant
    for orig in pd.unique(data['participants']['original_pid']):
        idx = data['participants'].original_pid == orig
        data['participants'].loc[idx,'participant'] = max_known_pid
        max_known_pid += 1

    # reset other tables pids
    for table in ['assignment']:
        T, P = data[table], data['participants']
        for orig in pd.unique(P.original_pid):
            table_idx = T.participant == orig
            new = P.loc[P.original_pid==orig, 'participant']
            T.loc[table_idx, 'participant'] = list(new)[0]
    

    # init df or append rows
    if num == 0:
        participants = data['participants']
        assignment    = data['assignment']
        #generation   = data['generation']
    else:
        participants = pd.concat([participants,data['participants']], ignore_index = True)
        assignment    = pd.concat([assignment,data['assignment']], ignore_index = True)
        #generation   = pd.concat([generation,data['generation']], ignore_index = True)

# create original participant number mapping
original_pids = participants[['participant', 'original_pid']]


##Create column of categories
#Rename some columns for convenience
participants = participants.rename(columns={'categories':'categoriesIdx','condition':'conditionStr'})
participants['categories'] = participants['categoriesIdx']
#participants['condition'] = participants['conditionStr']

#The last line in this loop shows a warning message,
# but I think it's harmless. I'll disable the message with
# this line
pd.options.mode.chained_assignment = None  # default='warn'
for idx, row in participants.iterrows():
    #Extract stimuli separated into categories
    catIdxA = np.array(eval(row.categoriesIdx))==0 #eval because it's saved as str
    catIdxB = np.array(eval(row.categoriesIdx))==1 #eval because it's saved as str
    sr = np.array(eval(row.stimuli))
    cats = [list(sr[catIdxA]),list(sr[catIdxB])]
    participants.categories.iloc[idx] = cats


#Change condition strings to numbers
mapcondData = [[0, 'Middle'], [1, 'Bottom']]
mapcond = pd.DataFrame(data = mapcondData, columns = ['condition','conditionStr'])
participants = pd.merge(participants,mapcond,on = 'conditionStr')

## Add correct response column to assignment
assignment = assignment.rename(columns={'response':'assignment'})

# remove irrelevant cols from various dfs
participants.drop(['timetaken','counterbalance','lab','original_pid','catflip','pptmatch','conditionStr','categoriesIdx','stimuli'],
		axis = 1, inplace=True)
assignment.drop(['rt','correctcat'], axis = 1, inplace=True)

#Merge data
assignment = pd.merge(participants,assignment,on = 'participant')

stimuli = stimuli.as_matrix()

trials = Simulation.Trialset(stimuli)
trials = trials.add_frame(assignment,task = 'assign')

with open('pickles/catassign.p','wb') as f:
	pickle.dump(trials, f)
