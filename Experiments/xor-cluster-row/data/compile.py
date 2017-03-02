import pandas as pd
import numpy as np
import os
import sqlite3

from Classes import Participant, Conditions

execfile('Imports.py')
import Modules.Funcs as funcs

dbfile = 'experiment.db'
sqlopts = dict(if_exists = 'replace', index = False)

skip_nums = [
			'5012', # seemed like a speed-through
			'5032', # cheated the generate program
			]

originals = [i for i in os.listdir('subjects') if i.endswith('.csv')	]

# get participants
part_objs = []
for i, fname in enumerate(originals):
	path = os.path.join('subjects',fname)

	_, pnum, condition = fname.split('-') 
	if pnum in skip_nums: continue
	if '4' in condition: continue

	p = Participant(path)
	if not p.complete: continue

	part_objs.append(p)

# create stimulus table
# // 72 73 74 75 76 77 78 79 80
#  // 63 64 65 66 67 68 69 70 71
#  // 54 55 56 57 58 59 60 61 62
#  // 45 46 47 48 49 50 51 52 53
#  // 36 37 38 39 40 41 42 43 44
#  // 27 28 29 30 31 32 33 34 35
#  // 18 19 20 21 22 23 24 25 26
#  //  9 10 11 12 13 14 15 16 17
#  //  0  1  2  3  4  5  6  7  8
values = np.linspace(-1,1, 9)
stimuli = np.fliplr(funcs.cartesian([values, values]))
stimuli = pd.DataFrame(stimuli, columns = ['F1', 'F2'])
stimuli.index.rename('stimulus')


# compile for sqlite
con = sqlite3.connect(dbfile)

# compile participants table
participants = pd.DataFrame(data=None,
	columns = ['participant','condition', 'start', 'finish'])

generation = pd.DataFrame(data=None,
	columns = ['participant','stimulus','trial','rt'])

betastats = pd.DataFrame(data=None,
	columns = ['participant',
	'area','between','within','xrange','xstd','yrange','ystd','drange','correlation'])

for ss in part_objs:
	row = ss.attrs2dict(participants.columns.values)
	participants = participants.append(row, ignore_index = True)

	rows = ss.generation[generation.columns.values]
	generation = generation.append(rows, ignore_index = True)

	# compute beta stats
	alphas = stimuli.as_matrix()[ss.alphas,:]
	betas = stimuli.as_matrix()[ss.generation.stimulus,:]	

	stats = funcs.stats_battery(betas, alphas = alphas)
	stats['participant'] = ss.participant
	betastats = betastats.append(stats,ignore_index = True)

for j in ['participant', 'start', 'finish']:
	participants[j] = participants[j].astype(int)

for j in ['participant','stimulus','trial']:
	generation[j] = generation[j].astype(int)

betastats['participant'] = betastats['participant'].astype(int)

# add tables
Conditions.to_sql('alphas', con, **sqlopts)
participants.to_sql('participants', con, **sqlopts)
generation.to_sql('generation', con, **sqlopts)
betastats.to_sql('betastats', con, **sqlopts)
stimuli.to_sql('stimuli', con, **sqlopts)


con.close()
