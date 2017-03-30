# Data was obtained from Alan Jern's github page:
# https://github.com/alanjern/categorygeneration-cogpsych-2013/tree/master/Experiments%203%20and%204/Data/Experiment%203
# 
# This script converts the matlab-formatted data 
# into a more useful sql format.

import pandas as pd
import os
from JK13Classes import JK13Participant

# list all mat files
matfile_dir = 'mat-files'
matfiles = [os.path.join(matfile_dir, i) 
	for i in os.listdir(matfile_dir) 
	if i.endswith('.mat')
]

# iterate over mat files
for pid, path in enumerate(matfiles):

	participant = JK13Participant(path)
	participant.training['participant'] = pid
	participant.generation['participant'] = pid
	print participant.training
	lll
	# init dataframes
	if pid == 0:
		training = pd.DataFrame(columns = participant.training.columns.values)
		generation = pd.DataFrame(columns = participant.generation.columns.values)

	training = training.append(participant.training, ignore_index = True)
	generation = generation.append(participant.generation, ignore_index = True)

print training.groupby('condition').describe()



