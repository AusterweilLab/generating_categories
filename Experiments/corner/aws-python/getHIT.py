# This is the value you reeceived when you created the HIT
# You can also retrieve HIT IDs by calling GetReviewableHITs
# and SearchHITs. See the links to read more about these APIs.
import boto.mturk.connection
import numpy as np
execfile('../analysis/Imports.py')
import Modules.Funcs as funcs
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
else:  #anything else but 'live' will send to sandbox
    HOST = hostsand

#HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
#HOST = 'mechanicalturk.sandbox.amazonaws.com'
#HOST = 'mechanicalturk.amazonaws.com'

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

#hit_id = "3B623HUYJ5QM7WRV82A0Z454ZZ8S8X"#"32ZCLEW0B0KEEL7M7P2C0D4GHM4PJD"

#Get all hits and iterate over them
allHITs = mtc.get_all_hits();

#Get matchlist
#matchdb='../data_utilities/cmp_midbot.db'
#list = funcs.getMatch('all',matchdb)[:,0]
#listcheck = np.zeros(len(list),dtype=bool)  
#listdone = [0,5,6,7,9,10,11,12,13] #the first 9 from hit 3B623HUYJ5QM7WRV82A0Z454ZZ8S8X
listdone = []

hitlist = [];
for hit in allHITs:    #Build hitlist
    hitlist.append(hit.HITId)
    #if hit.HITId != hit_id:
        #mtc.disable_hit(hit.HITId)

for hit_id in hitlist:
    assignments = mtc.get_assignments(hit_id)
    for assignment in assignments:
        assignmentID = assignment.AssignmentId
        worker_id = assignment.WorkerId
        submit_time = assignment.SubmitTime
        timetakenMins = '?'
        bonusDue = 0;
        print 'Assignment: ' + assignmentID
        print 'Worker:     ' + worker_id
        print 'HitID:      ' + hit_id        
        #print submit_time    
        for answer in assignment.answers[0]:
            print answer.qid + ': ' + str(answer.fields[0])
            if answer.qid == 'timetaken':
                timetaken = answer.fields[0]
                timetakenMins = round(float(timetaken)/60000,2)
                bonusDue = np.ceil(float(timetakenMins)/10)-1
            # if answer.qid == 'matchppt':
            #     listdone.append(int(answer.fields[0]))
        print 'Time taken: ' + str(timetakenMins) + ' mins'
        print 'BonusDue: $' + str(bonusDue)
        print '-----------'

#mtc.close()

allHITs = mtc.get_all_hits();
for hit in allHITs:
    print 'HIT ID: ' + hit.HITId
    print 'HIT Status: ' + hit.HITStatus
    print 'Title: ' + hit.Title
    print 'Max Assn. ' + hit.MaxAssignments
    print 'Num Assn. Available: ' + hit.NumberOfAssignmentsAvailable
    print 'Num Assn. Completed: ' + hit.NumberOfAssignmentsCompleted    
    print 'Num Assn. Pending: ' + hit.NumberOfAssignmentsPending    
    print '\n'

# for j in listdone:
#     listcheck = listcheck | (list==j)
# listundone = list[~listcheck]
# n_undone = len(listundone)
# print 'Still to go (total {}): {}'.format(str(n_undone), str(listundone))
