#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This script assigns a participant number, experiment condition
# and counterbalance condition.
# - - - - - - - - - - - - - - - - - - - - - - - -

# get globals
execfile('config.py')

# open connection
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

# 'touch' the file so it is reserved
path = os.path.join(destination, str(participant_num) + '.json')
open(path, 'a').close()


# - - - - - - - - - - - - - - - - - - - - - - - -
# Get the next condition number

# count participants in each condition
# only count participants who are marked as 'complete'

cmd = """
    SELECT COUNT(Condition)
    FROM Assignments 
    WHERE Complete = 1 
    AND Condition = ?
"""

counts = dict()
for i in conditions:
    c.execute(cmd,(i,))
    counts[i] = c.fetchone()[0] + 1

# condition is weighted choice based on counts
counts = invertcounts(counts)
participant_cond = weightedchoice(counts)
if participant_cond[-2:] == '_C' :
    participant_stimtype = 'Circles'
else:
    participant_stimtype = 'Squares'

# - - - - - - - - - - - - - - - - - - - - - - - -
# Get the next counterbalance condition number

cmd = """
    SELECT COUNT(Counterbalance)
    FROM Assignments
    WHERE Complete = 1
    AND Condition = ?
    AND Counterbalance = ?
"""

counts = dict()
for i in counterbalances:
        c.execute(cmd,(participant_cond, i))
        counts[str(i)] = c.fetchone()[0] + 1

# Counterbalance is weighted choice based on counts
counts = invertcounts(counts)
participant_counter = int(weightedchoice(counts))

# - - - - - - - - - - - - - - - - - - - - - - - -
# Get the next gentype condition number

cmd = """
SELECT COUNT(Gentype)
FROM Assignments
WHERE Complete = 1
AND Condition = ?
AND Counterbalance = ?
AND Gentype = ?
"""

counts = dict()
for i in gentypes:
        c.execute(cmd,(participant_cond, participant_counter,i))
        counts[str(i)] = c.fetchone()[0] + 1

# gentype is weighted choice based on counts
counts = invertcounts(counts)
participant_gentype = int(weightedchoice(counts))
##NOTE for the corner experiment with squares and circles, we don't care about gentype, so set this to
## the default that is 1. That is, generate betas
participant_gentype = 1

# - - - - - - - - - - - - - - - - - - - - - - - -
# write participant to database
data = (participant_num, participant_cond, participant_counter, participant_gentype, False)
c.execute('INSERT INTO Assignments VALUES (?,?,?,?,?)', data)
conn.commit()
conn.close()


# - - - - - - - - - - - - - - - - - - - - - - - -
# return data to client
data = dict(
    status = 'go',
    data = dict(
        participant = participant_num, 
        condition = participant_cond,
        stimtype = participant_stimtype,
        counterbalance = participant_counter,
        gentype = participant_gentype)    
)
print json.dumps(data)
sys.exit()
