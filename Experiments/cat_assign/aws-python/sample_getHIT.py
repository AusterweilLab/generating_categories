# This is the value you reeceived when you created the HIT
# You can also retrieve HIT IDs by calling GetReviewableHITs
# and SearchHITs. See the links to read more about these APIs.
import boto.mturk.connection

#HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
HOST = 'mechanicalturk.sandbox.amazonaws.com'
#HOST = 'mechanicalturk.amazonaws.com'

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

hit_id = "3B623HUYJ5QM7WRV82A0Z454ZZ8S8X"#"32ZCLEW0B0KEEL7M7P2C0D4GHM4PJD"

#Get all hits and iterate over them
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
    #if hit.HITId != hit_id:
        #mtc.disable_hit(hit.HITId)


result = mtc.get_assignments(hit_id)
assignment = result[0]
assignmentID = assignment.AssignmentId
worker_id = assignment.WorkerId
for answer in assignment.answers[0]:
    print answer.fields
    if answer.qid == 'answer':
        worker_answer = answer.fields[0]
        print "The Worker with ID {} and assignment ID {}  gave the answer {}".format(worker_id, assignmentID,worker_answer)


              
