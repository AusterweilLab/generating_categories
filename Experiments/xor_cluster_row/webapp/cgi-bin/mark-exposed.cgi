#! /bin/python
print "Content-Type: text/html"	# html is following
print 													# blank line, end of headers

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This script adds a new record to the workers database
# - - - - - - - - - - - - - - - - - - - - - - - -

# these worker IDs will not be added to the table
debug_workers = [
						'NOLANDEBUG123', # Debug
						'ATROS9SFZ8929' # Nolan's Account
					]

# set up worker database info
workerdb = dict(
		host = 'localhost', 
		port = 3306, 
		user = 'http', 
		db   = 'Workers',
	)


# ------------------
# Add packages
import cgitb
cgitb.enable()
import json, sys, time, pymysql


# ------------------
# get input from client
data = json.load(sys.stdin)
data['UnixTime'] = int(time.time())


# ------------------
# check if this is a lab member debugging! 
# if so, skip the check
if data['workerId'] in debug_workers:
	print json.dumps(dict(status = 'lab'))
	sys.exit() 


# ------------------
# Otherwise, construct a SQL command
command = """
INSERT into Workers (%s) 
VALUES (%s);
"""

# keys must have backticks: `KEY`
# values must have single quotes: 'VALUE'
keys, values = [], []
for k, v in data.items():
	keys += ["`" + k + "`"]
	values += ["'" + str(v) + "'"]

args = ( 
	','.join(keys), 
	','.join(values)	
	)


# ------------------
# connect to database
conn = pymysql.connect(**workerdb)
cur = conn.cursor()


# ------------------
# try to add the worker
# let client know if was an error
try:
	cur.execute(command % args)
	conn.commit()
	print json.dumps(dict(status = 'success'))

except:
	print json.dumps(dict(status = 'error'))


# ------------------
# Close out
cur.close()
conn.close()
sys.exit()