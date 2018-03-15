#Repeatedly send microbatches to AMT until desired condition is met. The
#condition for this experiment would be to exhaust the list of matched ppt data.
#130318 start
import numpy as np
import time
execfile('../analysis/Imports.py')
import Modules.Funcs as funcs

#Get list
matchdb='../data_utilities/cmp_midbot.db'
list = funcs.getMatch('all',matchdb)[:,0]


listcheck = np.zeros(len(list),dtype=bool)
listdone = [0,5,6,7,9,10,11,12,13] #the first 9 from hit 3B623HUYJ5QM7WRV82A0Z454ZZ8S8X
#Difficult to check server for which mathed ppt is done, so I'll skip that for
#now. It will suffice to simply repaet batches of 9 until I reach 122 or so.
batch_duration = 2*60*60 #in seconds #small amount for testing
check_interval_time = 10*60 #check every ten mins if number of assignments pending is zero. If so, run next hit.
force_expiry_interval = 12 #for expiry on current batch after this many intervals
time_between_hits = 1*10
n_undone = len(list)

for i in range(15):
    assignments_per_batch = min(n_undone,9) #Note that this overwrites the default in setHIT.py
    #Set HIT
    execfile('setHIT.py')
    curr_hit_id = hit_id #save hit_id from setHIT.py script
    #print i
    #Let timer run
    check_interval_count = 0
    while check_interval_count < force_expiry_interval:
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
    #Update listdone
    allHITs = mtc.get_all_hits();
    for hit in allHITs:
        hit_id = hit.HITId
        assignments = mtc.get_assignments(hit_id)
        for assignment in assignments:
            for answer in assignment.answers[0]:
                if answer.qid == 'matchppt':
                    listdone.append(int(answer.fields[0]))
    for j in listdone:
        listcheck = listcheck | (list==j)
    listundone = list[~listcheck]
    n_undone = len(listundone)
    print 'Still to go (total {}): {}'.format(str(n_undone), str(listundone))
    if n_undone < 1:
        break
    #Wait some time before setting next hit
    time.sleep(time_between_hits)
