#Approve all assignments in a given hit id
import boto.mturk.connection
#HOST = 'mechanicalturk.sandbox.amazonaws.com'
HOST = 'mechanicalturk.amazonaws.com'

#hit_id = '3B623HUYJ5QM7WRV82A0Z454ZZ8S8X';
mtc = boto.mturk.connection.MTurkConnection(host=HOST)



feedback2worker = 'Thanks for completing the task!'
allHITs = mtc.get_all_hits()

assignments_topay = [];
assignments_tobonus = [];
for hit in allHITs:
    hit_id = hit.HITId
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
        print 'Time taken: ' + str(timetakenMins) + ' mins'
        print 'BonusDue: $' + str(bonusDue)
        print '-----------'
        #save only assignments submitted for approval
        if assignment.AssignmentStatus == 'Submitted':
            assignments_topay.append(assignmentID)
        if bonusDue>0:
            assignment_tobonus.append(assignmentID)
        

hitObj = mtc.get_hit(hit_id)
reward = hitObj[0].FormattedPrice
testpass = raw_input('You are about to pay all ' + str(len(assignments_topay)) + ' of these participants ' + reward + ' each (base amount).\nTo continue, type \'yes\': ')
if testpass=='yes':
    paypass = True
else:
    paypass = False

#Just approve all assignments since if they submitted it probably means they did the task (unless they had some hacky way of doing it, but I'm not going to worry about that right now). Give some nice feedback.
if paypass:
    for assignment in assignments:
        assignmentID = assignment.AssignmentId
        worker_id = assignment.WorkerId
        hit_id = assignment.HITId
        print 'Approving worker {} for assignment {} (HIT {}).'.format(worker_id,assignmentID,hit_id)



# Get balance and print
balance = mtc.get_account_balance()
print 'Balance remaining: ' + str(balance)

# Look at bonuses

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

