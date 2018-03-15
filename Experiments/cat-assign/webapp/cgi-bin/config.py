import cgitb
cgitb.enable()
import json, sys, os, sqlite3, random
import numpy as np

print "Content-Type: text/html"			# HTML is following
print 															# blank line, end of headers

# - - - - - - - - - - - - - - - - - - - - - - - -
# USER SHOULD SET THESE PARAMETERS
# This is where all the data is stored (X.json and workers.db) 
#destination = "/var/services/homes/xian/CloudStation/data/generate-categories"
#destination = "../../datatemp"
destination = "/var/services/homes/xian/CloudStation/data/generate-categories"
assignmentdb = destination + "/assignments.db"

# Prepare to load stimuli db (from the earlier experiments
stimuliset = 'midbot'
stimulidb = destination + "/cmp_" + stimuliset + '.db'

# what are the conditions?
conditions = ['Middle', 'Bottom']
counterbalances = range(8)

#  ----- DATA ORGANIZATION -----
# Database: ~/CloudStation/data/assignments.db
# 	sqlite database with columns:
# 		Participant,Condition,Counterbalance,Complete
# 
# [PARTICIPANT_NUMBER].json
# 	This contains the 'actual' data as an arbitrarily formatted 
# 	JSON string.

# - - - - - - - - - - - - - - - - - - - - - - - -
# create the data folder if it doesn't exist
if not os.path.isdir(destination):
	os.mkdir(destination)
	os.chmod(destination,0775)

# - - - - - - - - - - - - - - - - - - - - - - - -
# also make worker DB if it doesn't exist
if not os.path.isfile(assignmentdb):
	conn = sqlite3.connect(assignmentdb)
	c = conn.cursor()
	cmd = '''CREATE TABLE Assignments
	(Participant INTEGER, 
        MatchedPpt INTEGER,
        Stimuli VARCHAR,
        Categories VARCHAR,
	Condition TEXT, 
	Counterbalance INTEGER, 
        Catflip INTEGER,
	Complete INTEGER)'''
	c.execute(cmd)
	conn.commit()
	conn.close()
	os.chmod(assignmentdb,0775)

# custom weighted choice function
def weightedchoice(counts):
	seq = []
	for i in counts.keys():
		seq += [i]*counts[i]
	return random.choice(seq)


# convert condition-wise counts into relative counts 
# suitable for the for choice function
def invertcounts(counts):        
	result = dict(counts)

	# inverted count is the sum of the counts for all OTHER groups
	for j in result.keys():
		result[j] = sum([counts[k] for k in counts.keys() if k!=j])
	
	# subtract min so that the smallest value is 1
	minval = min([v for v in result.values()])
	for j in result.keys():
		result[j] -= minval - 1
		
	return result
