#Approve all assignments in a given hit id
import boto.mturk.connection
#HOST = 'mechanicalturk.sandbox.amazonaws.com'
HOST = 'mechanicalturk.amazonaws.com'

hit_id = '3B623HUYJ5QM7WRV82A0Z454ZZ8S8X';
mtc = boto.mturk.connection.MTurkConnection(host=HOST)



feedback2worker = 'Thanks for completing the task!'

assignments = mtc.get_assignments(hit_id)
for assignment in assignments:
    assignmentID = assignment.AssignmentId
    worker_id = assignment.WorkerId
    submit_time = assignment.SubmitTime
    timetakenMins = '?'
    bonusDue = 0;
    print worker_id
    print submit_time    
    for answer in assignment.answers[0]:
        print answer.fields
        if answer.qid == 'timetaken':
            timetaken = answer.fields[0]
            timetakenMins = timetaken/60000
            bonusDue = np.ceil(float(timetakenMins)/10)-1
    print 'Time taken: ' + str(timetakenMins)
    print 'BonusDue: ' + str(bonusDue)
    print '-----------'

hitObj = mtc.get_hit(hit_id)
reward = hitObj[0].FormattedPrice
testpass = raw_input('You are about to pay all ' + str(len(assignments)) + ' of these participants ' + reward + ' each (base amount).\nTo continue, type \'yes\': ')
if testpass=='yes':
    paypass = True
else:
    paypass = False

#Just approve all assignments since if they submitted it probably means they did the task (unless they had some hacky way of doing it, but I'm not going to worry about that right now). Give some nice feedback.
if paypass:
    for assignment in assignments:
        assignmentID = assignment.AssignmentId
        worker_id = assignment.WorkerId
        print 'Approving worker {} for assignment {}.'.format(worker_id,assignmentID)
        #mtc.approve_assignment(assignmentID,feedback2worker)


#sample grant bonus
#mtc.grant_bonus(worker_id,assignmentID,bonus,reason)
    
# assignments = mtc.get_assignments(hit_id)
# for assignment in assignments:
#     #assignment = result[i]
#     assignmentID = assignment.AssignmentId
#     worker_id = assignment.WorkerId
#     print assignmentID
#     for answer in assignment.answers[0]:
#         print answer.fields
#         if answer.qid == 'answer':
#             worker_answer = answer.fields[0]
#             print "The Worker with ID {} and assignment ID {}  gave the answer {}".format(worker_id, assignmentID,worker_answer)
#     print 'Currently still testing and not yet approving'

