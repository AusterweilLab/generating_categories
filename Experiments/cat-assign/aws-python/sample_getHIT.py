# This is the value you reeceived when you created the HIT
# You can also retrieve HIT IDs by calling GetReviewableHITs
# and SearchHITs. See the links to read more about these APIs.
import boto.mturk.connection

#HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
HOST = 'mechanicalturk.sandbox.amazonaws.com'
#HOST = 'mechanicalturk.amazonaws.com'

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

hit_id = "3CRWSLD91L4MUT16VM2PR5R7BB3MOX"#"32ZCLEW0B0KEEL7M7P2C0D4GHM4PJD"
result = mtc.get_assignments(hit_id)
assignment = result[0]
assignmentID = assignment.AssignmentId
worker_id = assignment.WorkerId
for answer in assignment.answers[0]:
    print answer.fields
    if answer.qid == 'answer':
        worker_answer = answer.fields[0]
        print "The Worker with ID {} and assignment ID {}  gave the answer {}".format(worker_id, assignmentID,worker_answer)

              
