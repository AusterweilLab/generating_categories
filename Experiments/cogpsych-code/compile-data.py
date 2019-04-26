# compile the data from the xor-cluster-row and middle-bottom experiments; put it in a
# format that is convenient for simulations

import pandas as pd
import sqlite3

pd.set_option('display.width', 200, 'precision', 2)


databases = [ '../xor-cluster-row/data/experiment.db',
                            '../middle-bottom/data/experiment.db'
                        ]

# KEEP:
keep_tables = [
    'stimuli',          # one copy
    'alphas',           # add columns
    'participants', # add rows; INCREMENET PID; ADD EXPERIMENT MARKER
    'betastats',        # add rows; INCREMENET PID
    'generation',       # add rows; INCREMENET PID
]

experiments = pd.DataFrame(columns = ['condition', 'experiment'], dtype = int)

max_known_pid = 0
for num, dbpath in enumerate(databases):

    with sqlite3.connect(dbpath) as con:
        data = dict((T, pd.read_sql('SELECT * FROM ' + T, con)) for T in keep_tables)

        
    # get the stimuli df, init the alphas
    if num == 0: 
        stimuli = data['stimuli']
        alphas  = data['alphas']

    # add alpha columns otherwise
    else:
        alphas = pd.concat([alphas, data['alphas']], axis=1)

    # update condition mapping
    rows = [ dict(condition=i, experiment=num) for i in data['alphas'].columns ]
    experiments = experiments.append(rows, ignore_index = True)

    # remap participant IDs
    data['participants']['original_pid'] = data['participants'].participant
    for orig in pd.unique(data['participants']['original_pid']):
        idx = data['participants'].original_pid == orig
        data['participants'].loc[idx,'participant'] = max_known_pid
        max_known_pid += 1

    # reset other tables pids
    for table in ['betastats', 'generation']:
        T, P = data[table], data['participants']
        for orig in pd.unique(P.original_pid):
            table_idx = T.participant == orig
            new = P.loc[P.original_pid==orig, 'participant']
            T.loc[table_idx, 'participant'] = list(new)[0]
    

    # init df or append rows
    if num == 0:
        participants = data['participants']
        betastats    = data['betastats']
        generation   = data['generation']
    else:
        participants = pd.concat([participants,data['participants']], ignore_index = True)
        betastats    = pd.concat([betastats,data['betastats']], ignore_index = True)
        generation   = pd.concat([generation,data['generation']], ignore_index = True)

# convert experiment num to integer
experiments['experiment'] = experiments['experiment'].astype(int)

# add experiment number to participants
participants = pd.merge(participants,experiments, on= 'condition')

# create original participant number mapping
original_pids = participants[['participant', 'original_pid', 'experiment']]

# remove irrelevant cols from various dfs
participants.drop(['start','finish','counterbalance','lab','original_pid'],
		axis = 1, inplace=True)
generation.drop(['rt'], axis = 1, inplace=True)
betastats.drop(['bottom_only','bottom_used','top_and_bottom','top_only','top_used'],
    axis = 1, inplace=True)

dbfile = 'experiments-pooled.db'
con = sqlite3.connect(dbfile)
experiments.to_sql(   'experiments',   con, index = False, if_exists = 'replace')
original_pids.to_sql( 'original_pids', con, index = False, if_exists = 'replace')
participants.to_sql(  'participants',  con, index = False, if_exists = 'replace')
generation.to_sql(    'generation',    con, index = False, if_exists = 'replace')
stimuli.to_sql(       'stimuli',       con, index = False, if_exists = 'replace')
alphas.to_sql(        'alphas',        con, index = False, if_exists = 'replace')
betastats.to_sql(     'betastats',     con, index = False, if_exists = 'replace')
con.close()

