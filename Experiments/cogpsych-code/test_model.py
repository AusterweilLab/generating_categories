import pickle, sys, os
import pandas as pd
import numpy as np
import time
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13


# Specify default dataname
dataname_def = 'nosofsky1986'
participant_def = 'all'
unique_trials_def = 'all'
nchunks = 1000 #number of CHTC instances to run
#Allow for input arguments at the shell
narg = len(sys.argv)

if __name__ == "__main__" and narg>1:

        # if len(sys.argv)<4:
        #         unique_trials = unique_trials_def
        # else:
        #         unique_trials = int(sys.argv[3])
        # if len(sys.argv)<3:
        #         participant = participant_def
        # else:
        #         participant = int(sys.argv[2])
        # if len(sys.argv)<2:
        #         dataname = dataname_def
        # else:
        #         dataname = sys.argv[1]
        dataname = dataname_def
        participant = participant_def
        unique_trials = unique_trials_def

else:
        dataname = dataname_def
        participant = participant_def
        unique_trials = unique_trials_def

execfile('validate_data.py')
# get data from pickle
with open(pickledir+src, "rb" ) as f:
	trials = pickle.load( f )

trials.task = task
trials = Simulation.extractPptData(trials,participant,unique_trials)
