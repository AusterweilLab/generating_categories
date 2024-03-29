import json, sqlite3, os, sys
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull

os.chdir(sys.path[0])

pd.set_option('display.width', 200)
pd.set_option('display.precision', 2)

#my_import_loc = '/home/jausterw/work/generating_categories/Experiments/xor_cluster_row/analysis/Imports.py'

#execfile('Imports.py')
exec(open('Imports.py').read())
import Modules.Funcs as funcs

db_dst = '../data/experiment.db'
assignmentdb = '../data/assignments.db'
exclude = [
	]


# get worker info
c = sqlite3.connect(assignmentdb)
assignments = pd.read_sql('SELECT * from assignments', c)
c.close()

# first, find json files from ID belonging to people who
# are marked as complete and without a previous exposure
data = []
for i, row in assignments.iterrows():
	
	if row.Complete!=1: continue

	# skip if data file does not exist or is manually excluded
	pid = int(row.Participant)
	path = '../data/' + str(pid) + '.json'
	if pid in exclude: continue
	if not os.path.exists(path): continue

	with open(path,'r') as fh:
		S = fh.read()
		
		try: json.loads(S)
		except ValueError: 
			S = S[:-25]
			print(pid, json.loads(S)['info']['browser'])

	pdata = json.loads(S)
	if pdata['info']['lab']: continue

	data.append(json.loads(S))

# create participant table
rows = []
for i in data:
	r = dict(i['info'])
	del r['browser']
	rows.append(r)

participants = pd.DataFrame(data = rows)
del participants['exposed']


# create generated categories table
rows = []
for i in data:
	for j in i['generation']:
		row = i['generation'][j]
		row['participant'] = i['info']['participant']
		rows.append(row)
generation = pd.DataFrame(rows, dtype = int)

# create generalization table
rows = []
for i in data:
	for j in i['generalization']:
		row = i['generalization'][j]
		row['participant'] = i['info']['participant']
		row['response'] = row['response'] == 'Beta'
		rows.append(row)
generalization = pd.DataFrame(rows, dtype = int)


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
stimuli = np.fliplr(funcs.ndspace(9, 2))
stimuli = pd.DataFrame(stimuli, columns = ['F1', 'F2'])
stimuli.index.rename('stimulus')


# counterbalance table
counterbalance = pd.DataFrame([
	dict(counterbalance = 0, xax = 'size', yax = 'color', color = 'dark-light', size = 'small-big'), #
	dict(counterbalance = 1, xax = 'size', yax = 'color', color = 'light-dark', size = 'small-big'), #
	dict(counterbalance = 2, xax = 'size', yax = 'color', color = 'dark-light', size = 'big-small'), #
	dict(counterbalance = 3, xax = 'size', yax = 'color', color = 'light-dark', size = 'big-small'), #
	dict(counterbalance = 4, xax = 'color', yax = 'size', color = 'dark-light', size = 'small-big'), #
	dict(counterbalance = 5, xax = 'color', yax = 'size', color = 'light-dark', size = 'small-big'), #
	dict(counterbalance = 6, xax = 'color', yax = 'size', color = 'dark-light', size = 'big-small'), #
	dict(counterbalance = 7, xax = 'color', yax = 'size', color = 'light-dark', size = 'big-small'), #
])

# training examples table
alphas = pd.DataFrame(dict(
	XOR =     [ 0, 10, 70, 80],
	Cluster = [14, 16, 32, 34],
	Row =     [10, 12, 14, 16],
))

# compute beta category betastats for each participant
betastats = []
for pid, rows in generation.groupby('participant'):

	condition = participants.loc[participants.participant == pid, 'condition']
	betas = rows.stimulus
	#betas = stimuli.as_matrix()[betas,:]
	betas = stimuli.to_numpy()[betas,:]
	#p_alphas = alphas[condition].as_matrix()[:,0]
	#p_alphas = stimuli.as_matrix()[p_alphas,:]

	p_alphas = alphas[condition].to_numpy()[:,0]
	p_alphas = stimuli.to_numpy()[p_alphas,:]


	# stats battery
	stats = funcs.stats_battery(betas, alphas = p_alphas)
	stats['participant'] = pid

	betastats.append(stats)
betastats = pd.DataFrame(betastats)

#betastats.to_clipboard()
c = sqlite3.connect(db_dst)
participants.to_sql('participants', c, index = False, if_exists = 'replace', dtype ={'finish':'INTEGER'})
generation.to_sql('generation', c, index = False, if_exists = 'replace')
generalization.to_sql('generalization', c, index = False, if_exists = 'replace')
stimuli.to_sql('stimuli', c, index = False, if_exists = 'replace')
alphas.to_sql('alphas', c, index = False, if_exists = 'replace')
counterbalance.to_sql('counterbalance', c, index = False, if_exists = 'replace')
betastats.to_sql('betastats', c, if_exists = 'replace', index = False)
c.close()


