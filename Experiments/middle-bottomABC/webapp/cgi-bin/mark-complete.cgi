#! /bin/python

# get globals
execfile('config.py')
participant_num = json.load(sys.stdin)

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This script says 'goodbye' to the server. :-(
# 
# It basically marks a participant ID as complete, so that
# future participant assignments will be adjusted.
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

conn = sqlite3.connect(assignmentdb)
c = conn.cursor()
cmd = '''UPDATE Assignments SET Complete = ? WHERE Participant = ?'''
c.execute(cmd, (True, participant_num))
conn.commit()
conn.close()

