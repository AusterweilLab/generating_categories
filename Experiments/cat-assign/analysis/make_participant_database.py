# The indexing of participants in the cat-assign data and analysis is really
# confusing and tedious, so this script builds a database from which any
# participant number can be fetched. The appropriate types of indices to call
# can be:
#      old - this is the index applied to the midbot data (experiment 2)
#    match - numbers from old index are randomly allocated to this index. When
#            'pptmatch' appears in the dataset, it should be referring to
#            this.
# analysis - this is the index applied to the participants when analysed
#            (typically as a trialSet object)
# assigned - this is the index applied to the catassign category learning
#            experiment. It's the number that is displayed on the json file.
#            This shouldn't be used too much I think.
#150518

execfile('Imports.py')
import pickle
import Modules.Funcs as funcs
import sqlite3
import pandas as pd
import numpy as np

db_old      = '../../middle-bottom/data/experiment.db'
db_current  = '../data/experiment.db'
match_db = '../data_utilities/cmp_midbot.db'

allind = pd.DataFrame(columns = ['old','match','analysis','assigned'],dtype = int)

keep_tables = [
    'participants', # add rows; INCREMENT PID; ADD EXPERIMENT MARKER
]
with sqlite3.connect(db_old) as con:
    data_old = dict((T, pd.read_sql('SELECT * FROM ' + T, con)) for T in keep_tables)

with sqlite3.connect(db_current) as con:
    data_curr = dict((T, pd.read_sql('SELECT * FROM ' + T, con)) for T in keep_tables)

#Reproduce assignment of analysis indices from the compile-data-catassign.py
#file in cogpsych-code directory
data_temp = data_curr.copy()
data_temp['participants']['original_pid'] = data_temp['participants'].participant
max_known_pid = 0
for orig in pd.unique(data_temp['participants']['original_pid']):
    idx = data_temp['participants'].original_pid == orig
    data_temp['participants'].loc[idx,'participant'] = max_known_pid
    max_known_pid += 1

    
for pptOld in data_old['participants'].participant:
    pptMatch = funcs.getMatch(pptOld,match_db, fetch='match')
    pptAnalAssIdx = data_temp['participants']['pptmatch']==pptMatch
    if not pptAnalAssIdx.any():
        pptAnalysis = np.nan
        pptAssigned = np.nan
    else:
        pptAnalysis = data_temp['participants'].loc[pptAnalAssIdx]['participant'].item()
        pptAssigned = data_temp['participants'].loc[pptAnalAssIdx]['original_pid'].item()
        
    addrow = dict({'old':pptOld,
                   'match':pptMatch,
                   'analysis':pptAnalysis,
                   'assigned':pptAssigned})
    allind = allind.append(addrow, ignore_index = True)

#Convert the first two columns to int. Because analysis and assigned
# have NaNs, they'll have to remain as float.
allind = allind.astype({'old':int,'match':int})

savefilename = 'catassign_pptID.p'
with open(savefilename,'wb') as f:
    pickle.dump(allind,f)
