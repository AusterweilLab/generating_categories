#100419 Generalised version of construct-trial-set.py, alliwing terminal input to specify experiment to extract trials from. Use by typing  something like:
# $ python construct_trial_set xcr
# 
import sqlite3
import os
import pickle
import pandas as pd
import sys

execfile('Imports.py')

from Modules.Classes import Simulation

#Allow terminal input argument
narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    expName = sys.argv[1] #idx 1 arg from terminal is the experiment name
    compilation = False #by default not a compilation of exps
    if narg>2:
        compilation = sys.argv[2] #idx 2 must be Boolean and indicates if experiment db is a compilation of multiple exps
else:
    expName = 'corner' #default experiment name
    compilation = False

#This list of exps are known to be compilations:
if expName in ['pooled','5con','5con_s']:
    compilation = True

#Toggle construction of trialset pickle without first trial?
# This is in addition to the usual.
# Regular full set of trials is always constructed.
no1st = False

if compilation:
    pluralStr = 's'
else:
    pluralStr = ''

if len(expName)==0:
    expNameExt = ''
else:
    expNameExt = '-'
    
con = sqlite3.connect('experiment{}{}{}.db'.format(pluralStr,expNameExt,expName))
participants = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).values
con.close()

print('Extracting trialsets from experiment: {}'.format(expName))

# create categories mapping
mapping = pd.DataFrame(columns = ['condition', 'categories'])
for i in alphas.columns:
	As = alphas[i].values.flatten()
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

if expName == 'pooled':
    #Special cases where expname is not what used to be saved as pickles
    saveName = 'all_data_e1_e2'
elif expName == 'pooled-no1st':
    saveName = 'trials_2-4_e1_e2'
else:
    saveName = expName
    
with open('pickles/{}.p'.format(saveName),'wb') as f:
    pickle.dump(trials, f)

if no1st:
    # weed out all but last trials
    trials.Set = [i for i in trials.Set if len(i['categories'][1])>0]
    trials._update()

    with open('pickles/{}-no1st.p'.format(saveName),'wb') as f:
        pickle.dump(trials, f)

