#! /bin/python

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This script assigns a participant number, experiment condition
# and counterbalance condition.
# - - - - - - - - - - - - - - - - - - - - - - - -

# get globals
execfile('config.py')

# - - - - - - - - - - - - - - - - - - - - - - - -
# Open connection to current working db
conn = sqlite3.connect(assignmentdb)
c = conn.cursor()

# - - - - - - - - - - - - - - - - - - - - - - - -
# Get the next participant number

c.execute('SELECT max(Participant) FROM Assignments')
current_max = c.fetchone()[0]

if current_max == None:
	participant_num = 0
else:
	participant_num = current_max + 1

# in case there was a double-assignment, find an unused number
participant_file = os.path.join(destination, str(participant_num) + '.json')
while os.path.exists(participant_file):
	participant_num += 1
	participant_file = os.path.join(destination, str(participant_num) + '.json')



# - - - - - - - - - - - - - - - - - - - - - - - -
# Extract matched participant data
conMatch = sqlite3.connect(stimulidb)
cM = conMatch.cursor()

# Get maximum new_pid to allow for overflow
query = """
SELECT MAX(new_pid) 
FROM stimuli
"""
cM.execute(query)
max_new_pid = cM.fetchone()[0]+1 #plus one because it's indexed at 0

if participant_num >= max_new_pid:
        #Check for incomplete matchedppt and assign to curr pid        
        query = """
        SELECT MatchedPpt 
        FROM Assignments
        WHERE Complete = 0        
        """
        c.execute(query)
        matchlist_tup = c.fetchall()
        #convert from list of tuples to list of ints
        matchlist_int = [i[0] for i in matchlist_tup]

        if len(matchlist_int) > 0:        
                participant_match = random.choice(matchlist_int)
        else:
                #Randomly assign a match if everything is complete (to avoid angry workers)
                participant_match = random.choice(range(max_new_pid))

else:
        participant_match = participant_num

# Get stimulus, category, and condition
query = """
SELECT stimuli,category,condition,counterbalance 
FROM stimuli 
WHERE new_pid=
""" + str(participant_match)


cM.execute(query)
stimAll = cM.fetchall()
# Convert stim from list of tuples to list of ints
stim = [str(i[0]) for i in stimAll]
#stim = [[i[0] for i in stim if i[1]==ct] for ct in range(2)] #this makes stim = [[cat1stim,[cat2stim]]
cats = [str(i[1]) for i in stimAll]
#Randomise allocation of cat0/cat1 to alpha/beta
catflip = False
if random.random() <= .5:
        cats = [1-int(i) for i in cats]
        cats = [str(i) for i in cats]
        catflip = True
                

participant_cond = stimAll[0][2]
participant_counter = stimAll[0][3]
conMatch.close()

#Convert stim,cats to str because sql likes that
stimStr = '['+ ','.join(stim) + ']'
catsStr = '['+ ','.join(cats) + ']'


# - - - - - - - - - - - - - - - - - - - - - - - -
# 'touch' the file so it is reserved
path = os.path.join(destination, str(participant_num) + '.json')
open(path, 'a').close()




# - - - - - - - - - - - - - - - - - - - - - - - -
# write participant to database
data = (participant_num, participant_match,stimStr,catsStr, participant_cond, participant_counter, catflip, False)
c.execute('INSERT INTO Assignments VALUES (?,?,?,?,?,?,?,?)', data)
conn.commit()
conn.close()


# - - - - - - - - - - - - - - - - - - - - - - - -
# return data to client
data = dict(
	status = 'go',
	data = dict(
		participant = participant_num, 
                participant_match = participant_match,
                condition = participant_cond,
		counterbalance = participant_counter,
                catflip = catflip,
                stimuli = stimStr,                
                categories = catsStr)	
)
print json.dumps(data)
sys.exit()



