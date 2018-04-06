#Generate summary statistics for the catassign dataset

#Import stuff
import pickle, math
import pandas as pd
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from scipy.stats.stats import pearsonr

#Get learning data
data_assign_file = '../cat-assign/data/experiment.db'
con = sqlite3.connect(data_assign_file)
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * FROM assignment", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

#Compute and collate error rates
n = len(info)
error = pd.DataFrame(columns = ['participant','pptmatch','block0','block1','block2','block3','avgerror'])
for i, row in info.iterrows():
    #fh, ax = plt.subplots(1,2,figsize = (12,6))
    ppt  = row.participant
    pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
    nBaseStim = len(eval(row.categories))
    nTrials = len(pptAssign)
    nBlocks = nTrials / nBaseStim    
    blockIdx = np.array(range(nBlocks)).repeat(nBaseStim)
    pptmatch = row.pptmatch
    errorPpt = {'participant':pptmatch};
    errorlist = []
    for j in range(nBlocks):
        blockAssign = pptAssign.iloc[blockIdx==j]
        accuracyEl = float(sum(blockAssign.correctcat == blockAssign.response))/nBaseStim
        errorEl = 1-accuracyEl
        errorPpt['block'+str(j)] = errorEl
        errorlist.append(errorEl)
    #get matched data
    matchdb = '../cat-assign/data_utilities/cmp_midbot.db'
    matched = funcs.getMatch(pptmatch,matchdb)
    errorPpt['pptmatch'] = matched
    errorPpt['avgerror'] = np.mean(errorlist)
    error = error.append(errorPpt, ignore_index=True)



