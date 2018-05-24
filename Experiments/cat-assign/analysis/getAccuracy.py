#Present each participant's accuracy, followed by average accuracy
import pickle, math
import pandas as pd
import sqlite3
import numpy as np

#Get learning data
data_assign_file = '../data/experiment.db'
con = sqlite3.connect(data_assign_file)
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * FROM assignment", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

print('Ppt(Match)|  Error')
error = []
pptmatchlist = []

for i, row in info.iterrows():        
    pptmatchlist += [row.pptmatch]

pptmatchlist.sort()

for ppt in pptmatchlist:
    pptAssign = info['participant'].loc[info['pptmatch']==ppt].item();
    pptData = assignment.loc[assignment['participant']==pptAssign].sort_values('trial')
    nTrials = len(pptData)
    errorEl = 1 - (float(sum(pptData.correctcat == pptData.response))/nTrials)
    error += [errorEl]        
    print('{:10}|{:.3}'.format(ppt,errorEl))

print('Mean Error = {:.3}'.format(np.mean(error)))
print('Std  Error = {:.3}'.format(np.std(error)))
