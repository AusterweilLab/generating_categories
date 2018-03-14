# This is the value you reeceived when you created the HIT
# You can also retrieve HIT IDs by calling GetReviewableHITs
# and SearchHITs. See the links to read more about these APIs.
import boto.mturk.connection
import numpy as np
#HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
HOST = 'mechanicalturk.sandbox.amazonaws.com'
#HOST = 'mechanicalturk.amazonaws.com'

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

#hit_id = "3B623HUYJ5QM7WRV82A0Z454ZZ8S8X"#"32ZCLEW0B0KEEL7M7P2C0D4GHM4PJD"

#Get all hits and iterate over them
allHITs = mtc.get_all_hits();

hitlist = [];
for hit in allHITs:
    print 'HIT ID: ' + hit.HITId
    print 'HIT Status: ' + hit.HITStatus
    print 'Title: ' + hit.Title
    print 'Max Assn. ' + hit.MaxAssignments
    print 'Num Assn. Available: ' + hit.NumberOfAssignmentsAvailable
    print 'Num Assn. Completed: ' + hit.NumberOfAssignmentsCompleted    
    print 'Num Assn. Pending: ' + hit.NumberOfAssignmentsPending    
    print '\n'
    #Build hitlist
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
                timetakenMins = int(timetaken)/60000
                bonusDue = np.ceil(float(timetakenMins)/10)-1
        print 'Time taken: ' + str(timetakenMins) + ' mins'
        print 'BonusDue: ' + str(int(bonusDue))
        print '-----------'

#mtc.close()
