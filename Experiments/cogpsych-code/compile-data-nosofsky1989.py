# Construct the data from nosofsky 1986 as an sql db

import pandas as pd
import numpy as np
import pickle

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
#from scipy.spatial import ConvexHull

# KEEP:
keep_tables = [
    'stimuli',          # one copy
    'alphas',           # add columns
    'participants', # add rows; INCREMENET PID; ADD EXPERIMENT MARKER
    'betastats',        # add rows; INCREMENET PID
    'generation',       # add rows; INCREMENET PID
]

# create stimulus table
# 12 13 14 15
#  8  9 10 11
#  4  5  6  7  
#  0  1  2  3  
stimuli = np.fliplr(funcs.ndspace(4, 2)) #.ndspace(nlevels-of-feature,nfeatures)
stimuli = pd.DataFrame(stimuli, columns = ['F1', 'F2'])
stimuli.index.rename('stimulus')
stimuli = stimuli.as_matrix()

# generate ALL OF THE OBSERVED DATA!!
assignCat0 = np.array([[ 72, 255,  72,  73, 234,  66, 208, 226, #Size
                         23,  18,  55,  58,   2,   8,   3,   3,
                         79, 155,  48,   2,  81, 190,  60,   2, #Angle
                        262,  47,  11,   4,  76,  47,  24,   2, 
                         48,  94,  45, 162,  34,  34, 138,  47, #Crisscross
                         53, 120,  33,  24, 180,  44,  63,  41,
                         40, 200, 242,  83,  65,  49, 180,  70, #Diagonal
                          8,  57,  42, 199,   3,  27,  58,  55]]).transpose()

assignCat1 = np.array([[  2,   4,   2,   1,  35,   8,  39,  39, #Size
                         51,  56, 170, 179,  72, 229,  71,  71,
                          3, 116, 258,  80,   1,  97, 202,  80, #Angle
                         25,  35,  71, 259,   6,  35, 227,  80, 
                        168, 138,  29,  49,  40,  40, 102,  27, #Crisscross
                         21, 103,  41,  50,  52,  30, 160, 195,
                         46,  58,  25,   3, 228,  37,  77,  16, #Diagonal
                          78, 211,  44,  67,  83, 242, 171, 31]]).transpose()

assignMax = assignCat0 + assignCat1 #total assignments for each stimulus
ntrials = np.sum(assignMax)
stimulusIdx = np.tile(np.arange(16),(1,4)).transpose()
participantIdx = np.atleast_2d(np.arange(1).repeat(64)).transpose()
conditionIdx = np.tile(np.atleast_2d(np.arange(4).repeat(16)).transpose(),(1,1))

# Consolidate as data array
dataA = np.concatenate([participantIdx, stimulusIdx, assignCat0, conditionIdx],1)

# Build data frame with cols:
# participant, trial, stimulus, assignment, categories
# generation = pd.DataFrame(columns = ['participant','trial','stimulus','assignment']) #'categories' will be added at a later section

# Preallocate generation array (to be converted to dataframe later)
#generationA = np.zeros(shape=(ntrials,4))
generationA = np.repeat(dataA,assignMax.squeeze(),0)
trialCond = [];
for i,nResp in enumerate(assignMax):
    trialCond = trialCond + (range(nResp))

trialCond = np.atleast_2d(trialCond).transpose()

#Also construct global trial list (for total trial count for each participant)
trialG = [];
for i in range(2): #2 because sample size is 2
    trialGp = np.sum(generationA[:,0] == i)
    trialG += range(trialGp)

# Convert global trial list into an array range for concatenation
trialG = np.atleast_2d(trialG).transpose()

# to get category assignments, any trial number more than or equal to the first cat0 trials is considered
# to be assigned cat1
assignmentA = trialCond >= generationA[:,2:3]
#assignmentA = np.atleast_2d(assignmentA).transpose()

generationA = np.concatenate([generationA[:,0:1],
                              trialG,
                              generationA[:,1:2],
                              assignmentA,
                              generationA[:,3:4]],1)

#Map conditions to the (trained) category exemplars for each condition
trainedExemplarsL = [[[ 1, 4, 6, 7],[    10, 11, 13]], #dimensional
                     [[    1, 5, 8],[ 2,  6, 11, 14]], #crisscross
                     [[ 3, 6, 9,12],[ 0,  1, 14, 15]], #intext
                     [[ 1, 2, 6,11],[ 4,  9, 13, 14]]]  #diagonal

# Generate list of conditions matched to each row of assigned frequencies
conditionsBase  = np.array([[0,1,2,3]])#np.array([['Dimensional','Criss-Cross','Interior-Exterior','Diagonal']])
conditions = np.array(conditionsBase).repeat(8,1).transpose()
#conditions = np.tile(conditions,[2,1]);

mapping = pd.DataFrame(columns = ['condition','categories'])
#map conditions to each trainedexemplar set
for i,con in enumerate(conditionsBase[0]):
    mapping = mapping.append(
        dict(condition = con, categories = trainedExemplarsL[i]),
        ignore_index = True
    )

generation = pd.DataFrame(data = generationA,columns = ['participant','trial','stimulus','assignment','condition'])
generation = pd.merge(generation, mapping, on='condition')


#del generation['condition']

trials = Simulation.Trialset(stimuli)
trials = trials.add_frame(generation,task = 'assign')

with open('pickles/nosofsky1989.p','wb') as f:
    pickle.dump(trials, f)
