import sys, boto.mturk.connection, boto.mturk.qualification, datetime
with open('config.py') as f:
    exec(f.read())

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

# Delete any HIT with the same title
# HITs =  mtc.get_all_hits()
# for hit in HITs:
# 	if hit.Title == hitconfig['title']:
# 		print('Deleted HIT:')
# 		printHIT(hit)
# 		mtc.disable_hit(hit.HITId)

# Then, post a new HIT 
create_hit_result = mtc.create_hit(**hitconfig)
print('\nCreated HIT:')
HITs =  mtc.get_all_hits()
for hit in HITs:
	if hit.Title == hitconfig['title'] and hit.HITStatus == 'Assignable':
		printHIT(hit)

# HITs =  mtc.get_all_hits()
# for hit in HITs:
# 	if hit.Title == hitconfig['title']:
# 		printHIT(hit)
