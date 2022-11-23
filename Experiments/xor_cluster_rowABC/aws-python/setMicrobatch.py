#Repeatedly send microbatches to AMT until desired condition is met. The
#condition for this experiment would be to exhaust the list of matched ppt data.
#130318 start
import numpy as np
import time
execfile('../analysis/Imports.py')
import Modules.Funcs as funcs
import boto
from boto.mturk.connection import MTurkConnection
hostlive = 'mechanicalturk.amazonaws.com'
hostsand = 'mechanicalturk.sandbox.amazonaws.com'

#Take in inputs from shell
if __name__ == "__main__":
    import sys
    if len(sys.argv)>1:
        hosttype = sys.argv[1]
    else:
        hosttype = 'sandbox'
else:
    hosttype = 'sandbox'

if hosttype=='live':
    HOST = hostlive
else: #anything else but 'live' will send to sandbox
    HOST = hostsand


#Get list
#matchdb='../data_utilities/cmp_midbot.db'
#list = funcs.getMatch('all',matchdb)[:,0]

maxbatches = 10 #maximum number of batches to run
check_interval_time = 10*60 #check every ten mins if number of assignments pending is zero. If so, run next hit.
force_expiry_interval = 12 #for expiry on current batch after this many intervals
time_between_hits = 1*10

#Make first pass at what's not yet done
#HOST = 'mechanicalturk.amazonaws.com'
#HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = boto.mturk.connection.MTurkConnection(host=HOST)
    
# allHITs = mtc.get_all_hits();
# for hit in allHITs:
#     hit_id = hit.HITId
#     assignments = mtc.get_assignments(hit_id)
#     for assignment in assignments:
#         for answer in assignment.answers[0]:            
#             if answer.qid == 'code':
#                 if answer.fields[0]=='Finished':
#                     listdone.append(int(answer.fields[0]))

#However, maybe due to submission issues on the client end (there really shouldn't be too many...), there can be completed data sets that are not registered on the AMT end. If so, manually include them in this list here to be treated as done.
# manual_donelist = [47,88]
# listdone += manual_donelist

# for j in listdone:
#     listcheck = listcheck | (list==j)
# listundone = list[~listcheck]
#n_undone = len(listundone)

for i in range(maxbatches):
    assignments_per_batch = 9 #Note that this overwrites the default in setHIT.py
    #Set HIT
    execfile('setHIT.py')
    curr_hit_id = hit_id #save hit_id from setHIT.py script
    #print i
    #Let timer run
    check_interval_count = 0
    while check_interval_count < force_expiry_interval:
        check_interval_count += 1
        time.sleep(check_interval_time)        
        #Run check after timeout - if number
        #of assignments in hit is satisfied, break from loop
        nAss = len(mtc.get_assignments(curr_hit_id))
        print 'Checking HIT ' + curr_hit_id + ' on ' + time.strftime('%X %x') + '. ' + str(nAss) + ' assignments done on this hit.'
        if nAss>=assignments_per_batch:
            break
        #time.sleep(batch_duration)
    #Expire HIT
    mtc.expire_hit(curr_hit_id) #mtc and hit_id comes from the setHIT.py script
    time.sleep(time_between_hits)
    #Update listdone
    # allHITs = mtc.get_all_hits();
    # for hit in allHITs:
    #     hit_id = hit.HITId
    #     assignments = mtc.get_assignments(hit_id)
    #     for assignment in assignments:
    #         for answer in assignment.answers[0]:
    #             if answer.qid == 'matchppt':
    #                 listdone.append(int(answer.fields[0]))
    # for j in listdone:
    #     listcheck = listcheck | (list==j)
    # listundone = list[~listcheck]
    # n_undone = len(listundone)
    # print 'Still to go (total {}): {}'.format(str(n_undone), str(listundone))
    # if n_undone < 1:
    #     break
    #Wait some time before setting next hit

