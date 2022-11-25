# Data was obtained from Alan Jern's github page:
# https://github.com/alanjern/categorygeneration-cogpsych-2013/tree/master/Experiments%203%20and%204/Data/Experiment%203
# 
# This script converts the matlab-formatted data 
# into a more useful sql format.


import pandas as pd
import os,sys
from JK13 import JK13Participant
from JK13 import JK13
import sqlite3

os.chdir(sys.path[0])

exec(open('Imports.py').read())

# list all mat files
matfile_dir = 'mat-files'
matfiles = [os.path.join(matfile_dir, i) 
	for i in os.listdir(matfile_dir) 
	if i.endswith('.mat')
]

# iterate over mat files
for pid, path in enumerate(matfiles):

	participant = JK13Participant(path)
	stats = participant.stats()

	# add participant ids
	participant.training['participant'] = pid
	participant.generation['participant'] = pid
	stats['ranges']['participant'] = pid
	stats['distances']['participant'] = pid

	# init dataframes
	if pid == 0:
		training = pd.DataFrame(columns = participant.training.columns.values)
		generation = pd.DataFrame(columns = participant.generation.columns.values)
		ranges = pd.DataFrame(columns = ['participant', 'condition'] + JK13.features)
		distances = pd.DataFrame(columns = ['participant', 'condition', 'Within', 'Between'])

	# add data 
	training = training.append(participant.training, ignore_index = True)
	generation = generation.append(participant.generation, ignore_index = True)
	ranges = ranges.append(stats['ranges'], ignore_index = True)
	distances = distances.append(stats['distances'], ignore_index = True)


# save databases
con = sqlite3.connect('experiment.db')

dtypes = {'participant':'INTEGER', 'category':'INTEGER', 'stimulus':'INTEGER'}
training.to_sql('training', con, index = False, if_exists = 'replace', dtype = dtypes)

dtypes = {'participant':'INTEGER', 'stimulus':'INTEGER'}
generation.to_sql('generation', con, index = False, if_exists = 'replace', dtype = dtypes)

dtypes = {'participant':'INTEGER'}
ranges.to_sql('ranges', con, index = False, if_exists = 'replace', dtype = dtypes)
distances.to_sql('distances', con, index = False, if_exists = 'replace', dtype = dtypes)
con.close()


