import json, sqlite3, os, sys
import pandas as pd
import numpy as np
import datetime
from scipy.spatial import ConvexHull

pd.set_option('display.width', 200, 'precision', 2)

execfile('Imports.py')
import Modules.Funcs as funcs

db_dst = '../data/experiment.db'
assignmentdb = '../data/assignments.db'
exclude = [
	]


# get worker info
c = sqlite3.connect(assignmentdb)
workerInfo = pd.read_sql('SELECT * from assignments', c)
c.close()

# first, find json files from ID belonging to people who
# are marked as complete and without a previous exposure
data = []
for i, row in workerInfo.iterrows():
	
	if not row.Complete: continue

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
			print pid, json.loads(S)['info']['browser']

	pdata = json.loads(S)
	if pdata['info']['lab']: continue
        #print pdata['assignment']['0']['response']
	data.append(json.loads(S))

# create participant table
rows = []
for i in data:
	r = dict(i['info'])
        s = dict(i['submit'])
        #Compute time taken in mins (rounded up)
        timetaken = r['finish'] - r['start']
        r['timetaken'] = timetaken
        #Convert lists to str so that it can be stored in sql db
        r['categories'] = str(r['categories'])
        r['stimuli'] = str(r['stimuli'])
        if len(s)>0:
                r['age'] = s['age']
                r['sex'] = s['sex']                
                r['comments'] = s['comments']
        else:
                r['age'] = ''
                r['sex'] = ''                
                r['comments'] = ''

	del r['browser']
        #del r['finish']
        #del r['start']
	rows.append(r)

participants = pd.DataFrame(data = rows)
del participants['exposed']


# create generated categories table
# rows = []
# for i in data:
# 	for j in i['generation']:
# 		row = i['generation'][j]
# 		row['participant'] = i['info']['participant']
# 		rows.append(row)

# generation = pd.DataFrame(rows, dtype = int)

# create assignment table
rows = []
for i in data:
	for j in i['assignment']:
		row = i['assignment'][j]
		row['participant'] = i['info']['participant']
		#row['response'] = row['response'] == 'Beta'
		rows.append(row)
assignment = pd.DataFrame(rows, dtype = int)

#Print preliminary assignment stats and amount to pay ppts
#execfile('printMatchList.py') # load getMatch function to plot stim space
matchdb='../data_utilities/cmp_midbot.db'
#funcs.getMatch(1,matchdb) #an example of getting a participant match
for i in range(14):
        assdata = assignment.loc[assignment['participant']==i]
        pptdata = participants.loc[participants['participant']==i]
        accuracy = float(sum(assdata['correctcat']==assdata['response']))/32;
        #accuracycum = assdata.correctcat
        if len(assdata)>0:
                #print 'len' + len(assdata)
                timetaken = int(np.ceil(pptdata.iloc[0]['timetaken']/60000)) #in minutes rounded up
                bonusDue = max(0,round(np.ceil(float(timetaken)/10))-1) #in dollars rounded up
                timestart = datetime.datetime.fromtimestamp(
                        int(pptdata.iloc[0]['start'])/1000
                ).strftime('%Y-%m-%d %H:%M:%S')
                timeend = datetime.datetime.fromtimestamp(
                        int(pptdata.iloc[0]['finish'])/1000
                ).strftime('%Y-%m-%d %H:%M:%S')

                print 'Ppt: ' + str(i) + ' Accuracy: ' + str(accuracy)
                print '\tAge: ' + str(pptdata.iloc[0]['age']) + ', Sex: ' + pptdata.iloc[0]['sex'] + ', Comments: ' + pptdata.iloc[0]['comments'] 
                print '\tTime taken: ' + str(timetaken) + ' mins, Bonus Due: $' + str(bonusDue)
                print '\tTime start: ' + timestart + ' ('+ str(pptdata.iloc[0]['start']/1000) + ')' 
                print '\tTime end: ' + timeend +  ' ('+ str(pptdata.iloc[0]['finish']/1000) + ')'

lll        
        


# create stimulus table
values = np.linspace(-1,1, 9)
stimuli = np.fliplr(funcs.cartesian([values, values]))
stimuli = pd.DataFrame(stimuli, columns = ['F1', 'F2'])
stimuli.index.rename('stimulus')

# // 72 73 74 75 76 77 78 79 80
#  // 63 64 65 66 67 68 69 70 71
#  // 54 55 56 57 58 59 60 61 62
#  // 45 46 47 48 49 50 51 52 53
#  // 36 37 38 39 40 41 42 43 44
#  // 27 28 29 30 31 32 33 34 35
#  // 18 19 20 21 22 23 24 25 26
#  //  9 10 11 12 13 14 15 16 17
#  //  0  1  2  3  4  5  6  7  8


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
	Middle = [30, 32, 48, 50 ],
	Bottom = [12, 14, 30, 32],
))

# compute beta category betastats for each participant
bottom_nums = range(9)
top_nums = range(72,81)
betastats = []
for pid, rows in goodness.groupby('participant'):

	condition = participants.loc[participants.participant == pid, 'condition']
	betas = rows.stimulus
	betas = stimuli.as_matrix()[betas,:]
	p_alphas = alphas[condition].as_matrix()[:,0]
	p_alphas = stimuli.as_matrix()[p_alphas,:]

	# stats battery
	stats = funcs.stats_battery(betas, alphas = p_alphas)

	# compute top and bottom stats
	nums = rows.stimulus
	bottom_used = any(nums.isin(bottom_nums))
	bottom_only = all(nums.isin(bottom_nums))
	top_used = any(nums.isin(top_nums))
	top_only = all(nums.isin(top_nums))
	top_and_bottom = bottom_used & top_used

	attl_fields = dict(
							participant = pid, 
							bottom_used = bottom_used, bottom_only = bottom_only,
							top_used = top_used, top_only = top_only,
							top_and_bottom = top_and_bottom
							)
	stats.update(attl_fields)
	betastats.append(stats)
betastats = pd.DataFrame(betastats)


c = sqlite3.connect(db_dst)
participants.to_sql('participants', c, index = False, if_exists = 'replace', dtype ={'finish':'INTEGER'})
assignment.to_sql('assignment', c, index = False, if_exists = 'replace')
goodness.to_sql('goodness', c, index = False, if_exists = 'replace')
stimuli.to_sql('stimuli', c, index = False, if_exists = 'replace')
alphas.to_sql('alphas', c, index = False, if_exists = 'replace')
counterbalance.to_sql('counterbalance', c, index = False, if_exists = 'replace')
betastats.to_sql('betastats', c, if_exists = 'replace', index = False)
c.close()


