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
assignCat0 = np.array([[213, 253, 192, 218, 185, 193, 187, 162, #p1dimensional
                         24,  33,  31,  40,   0,   0,   0,   0,
                          7,  27, 183, 206,  58,  73, 152, 187, #p1crisscross
                        193, 147,  46,  66, 212, 149,  35,  13, 
                         19,  78,  76,  65,  36, 179, 161,  99, #p1intext
                         60, 206, 171, 101,  32, 128, 116,  39,
                        226, 231, 165,  92, 214, 206, 109,  44, #p1diagonal
                        208, 108,  31,  12, 209,  71,  13,   3,
                        196, 185, 214, 197, 155, 150, 152, 165, #p2dimensional
                         59,  86,  57,  58,   9,  11,   7,   4,
                         30,  95, 164, 192, 101,  88, 155, 169, #p2crisscross
                        176, 131,  62,  75, 199, 122,  22,  18,
                         14,  48,  54,  24,  38,  95,  89,  41, #p2intext
                         61, 131, 122,  33,  40,  70,  34,  15,
                        216, 199, 139,  41, 203, 193,  53,  14, #p2diagonal
                        219, 151,  36,   6, 189,  75,   6,   3,]]).transpose()

assignCat1 = np.array([[  4,   1,   2,   1,  57,  47,  40,  36, #p1dimensional
                        194, 198, 190, 181, 204, 235, 220, 258,
                        203, 187,  61,   9, 162, 151,  54,  47, #p1crisscross
                         21,  64, 155, 154,   4,  44, 214, 216, 
                        238, 162, 181, 219, 216,  72,  65, 159, #p1intext
                        189,  62,  75, 150, 238, 126, 157, 223,
                          0,  20,  69, 168,   6,  67, 151, 212, #p1diagonal
                         20, 135, 264, 245,  41, 191, 211, 258,
                          7,   4,   9,   8,  27,  35,  55,  51, #p2dimensional
                        120, 116, 135, 170, 193, 171, 195, 199,
                        190, 161,  26,  14, 139, 128,  70,  62, #p2crisscross
                         51, 118, 152, 147,  23, 101, 199, 219,
                        132,  81, 116, 118, 106,  40,  55,  99, #p2intext
                         83,  16,  45,  98, 106,  71, 101, 124,
                          3,  15,  58, 195,   5,  36, 178, 215, #p2diagonal
                         12,  67, 194, 237,  24, 143, 233, 241,]]).transpose()

assignMax = assignCat0 + assignCat1 #total assignments for each stimulus
ntrials = np.sum(assignMax)
stimulusIdx = np.tile(np.arange(16),(1,8)).transpose()
participantIdx = np.atleast_2d(np.arange(2).repeat(64)).transpose()
conditionIdx = np.tile(np.atleast_2d(np.arange(4).repeat(16)).transpose(),(2,1))

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
trainedExemplarsL = [[[ 0, 3, 5, 6],[ 9, 10, 12, 15]], #dimensional
                     [[ 3, 6, 9,12],[ 0,  5, 10, 15]], #crisscross
                     [[ 5, 6, 9,10],[ 2,  4, 11, 13]], #intext
                     [[ 2, 5, 8,12],[ 3,  7, 10, 13]]]  #diagonal

# Generate list of conditions matched to each row of assigned frequencies
conditionsBase  = np.array([[0,1,2,3]])#np.array([['Dimensional','Criss-Cross','Interior-Exterior','Diagonal']])
conditions = np.array(conditionsBase).repeat(8,1).transpose()
conditions = np.tile(conditions,[2,1]);

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


# with open('pickles/nosofsky1986.p','wb') as f:
# 	pickle.dump(trials, f)

####



# with open('pickles/nosofsky1986_p0.p','wb') as f:
# 	pickle.dump(trials_p0, f)
# with open('pickles/nosofsky1986_p1.p','wb') as f:
# 	pickle.dump(trials_p1, f)

#Also extract condition data
# generation_p0c = [[],[],[],[]]
# generation_p1c = [[],[],[],[]]
# for i in range(4):
#     generation_p0c[i] = generation_p0.loc[generation_p0['condition']==i]
#     generation_p1c[i] = generation_p1.loc[generation_p1['condition']==i]
#     trials_p0c = Simulation.Trialset(stimuli)
#     trials_p0c = trials_p0c.add_frame(generation_p0c[i], task = 'assign')
#     trials_p1c = Simulation.Trialset(stimuli)
#     trials_p1c = trials_p1c.add_frame(generation_p1c[i], task = 'assign')
#     with open('pickles/nosofsky1986_p0c'+str(i)+'.p','wb') as f:
# 	pickle.dump(trials_p0c, f)
#     with open('pickles/nosofsky1986_p1c'+str(i)+'.p','wb') as f:
# 	pickle.dump(trials_p1c, f)
        
##DONE! I think. Now to save the data as pickles, and then get the fitting to work.


    
# gct = 0; #global counter
# for idx in range(dataA.shape[0]):
#     participant = dataA[idx,0]
#     stimulus = dataA[idx,1]
#     cat0 = dataA[idx,2]
#     cat1 = dataA[idx,3]
#     trl = 0; #trial counter
#     for jdx in range(cat0):
#         assignment = 0
#         generationA[gct,:] = [participant, trl, stimulus, assignment]
#         trl += 1 #increment trial counter
#         gct += 1 #increment global counter
#     for jdx in range(cat1):
#         assignment = 1
#         generationA[gct,:] = [participant, trl, stimulus, assignment]
#         trl += 1 #increment trial counter
#         gct += 1 #increment global counter
                            
#Calculate probabilities of assigning cat 0 from the observed frequencies
# assignp = assignCat0 / (assignCat0 + assignCat1).astype(np.float)

# save dataframe tables into sql db
# stimuli.to_sql('stimuli', c, index = False, if_exists = 'replace')




