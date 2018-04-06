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
    #'betastats',        # add rows; INCREMENET PID
    'generation',       # add rows; INCREMENET PID
]

# create stimulus cube
#    6----7
#   /|   /|
#  2----3 |
#  | 4--|-5
#  |/   |/ 
#  0----1
# (drawing this cube is my proudest achievement)

#Map conditions to the (trained) category exemplars for each condition
trainedExemplarsL = [[[ 0, 1, 2, 3],[ 4, 5, 6, 7]], #Type I
                     [[ 2, 3, 4, 5],[ 0, 1, 6, 7]], #Type II
                     [[ 0, 2, 3, 7],[ 1, 4, 5, 6]], #Type III
                     [[ 0, 2, 3, 6],[ 1, 4, 5, 7]], #Type IV
                     [[ 0, 2, 3, 5],[ 1, 4, 6, 7]], #Type V
                     [[ 1, 2, 4, 7],[ 0, 3, 5, 6]]] #Type VI


stimuli = np.fliplr(funcs.ndspace(2, 3)) #.ndspace(nlevels-of-feature,nfeatures)
stimuli = pd.DataFrame(stimuli, columns = ['F1', 'F2', 'F3'])
stimuli.index.rename('stimulus')
stimuli = stimuli.as_matrix()
nstim = len(stimuli)
trials = 200
nconditions = len(trainedExemplarsL)
# generate ALL OF THE OBSERVED DATA!!
# Note that due to a lack of individual-level data, I will have to generate counts from probabilities
assignErr1 = np.array([[.010, .032, .061, .065, .075, .143]]).transpose() #this is the average data found on p355
assignErr0 = 1-assignErr1
assignCat0 = np.atleast_2d(np.array((assignErr*trials), dtype = int).repeat(nstim)).transpose()

trainedExemplarsFlat = np.array([exemplars for sublist in trainedExemplarsL for subsublist in sublist for exemplars in subsublist])
trainedExemplarsFlatCondIdx = np.arange(nconditions).repeat(8)
for condition in range(nconditions):
    currSelection = trainedExemplarsFlatCondIdx==condition
    currStim = assignCat0[currSelection]
    currTrainedExemplars = trainedExemplarsFlat[currSelection]
    #first four stim are cat 0, which should be changed
    currStim[currTrainedExemplars[0:4]] = trials-currStim[currTrainedExemplars[0:4]]
    assignCat0[currSelection] = currStim

assignCat1 = trials-assignCat1 #so artificial
#So here, cat1 is the only wrong category, and cat0 is the only correct category

assignMax = assignCat0 + assignCat1 #total assignments for each stimulus
ntrials = np.sum(assignMax)
#nstim = assignCat0.shape[0]/nconditions
stimulusIdx = np.tile(np.arange(nstim),(1,nconditions)).transpose()
participantIdx = np.atleast_2d(np.arange(1).repeat(nstim*nconditions)).transpose()
conditionIdx = np.tile(np.atleast_2d(np.arange(nconditions).repeat(nstim)).transpose(),(1,1))

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


# Generate list of conditions matched to each row of assigned frequencies
conditionsBase  = np.atleast_2d(np.arange(nconditions))#np.array([['Dimensional','Criss-Cross','Interior-Exterior','Diagonal']])
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
trials = trials.add_frame(generation,task = 'error')

with open('pickles/NGPMG1994.p','wb') as f:
    #pass
    pickle.dump(trials, f)
