#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
print "Content-Type: text/html"	# html is following
print 													# blank line, end of headers

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This script checks to see whether the workers is eligble to 
# participate.
# 
# Workers are ineligible if they have participated in a study 
# using the same paradigm within the last 14 days.
# - - - - - - - - - - - - - - - - - - - - - - - -

debug_workers = [
						'NOLANDEBUG123', # Debug
						'ATROS9SFZ8929', # Nolan's Account
    'A1G22IHEURCO4P' # Xian's Account
					]


# set up worker database
workerdb = dict(
		host='localhost', 
		port=3306, 
		user='http', 
		db='Workers'
	)

# ------------------
# Add packages
import cgitb
cgitb.enable()
import json, sys, time, pymysql


# ------------------
# get input from client
data = json.load(sys.stdin)

# get cutoff integer -- 14 days ago
# 86400 seconds per day * 14 days
cutoff = int(time.time()) - 86400 * 14 

# ------------------
# construct query
command = """
	SELECT workerId 
	FROM Workers 
	WHERE Paradigm = %s
	AND UnixTime > %s
	AND workerId = %s
"""
args = (data['Paradigm'], cutoff, data['workerId'])


# ------------------
#  connect to database and execute command
conn = pymysql.connect(**workerdb)
cur = conn.cursor()
cur.execute(command, args)
records = list(cur)
cur.close()
conn.close()


# ------------------
# check records and return result
# if worker does not exist, then records will be []
if not records or data['workerId'] in debug_workers: 
	output = dict(status = 'go')
else:
	output = dict(status = 'exposed')

print json.dumps(output)
sys.exit()
