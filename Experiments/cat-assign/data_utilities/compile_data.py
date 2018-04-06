# Extract data from given databases and compile them so participant data can be easily extracted for the cat-assign experiment
#Remember to Randomise the order of participants in each database before assignment to new participants
#Really, I don't think this randomness is necessary, but why not.
# Start 050318

#Do imports
import sqlite3
import pandas as pd
import random

#Load data
dbnames = ['xcr.db','midbot.db']
pref_ass = 'ass_'

pref_out = 'cmp_' #prefix for output db

for dbname in dbnames:
    con = sqlite3.connect(dbname)
    participants = pd.read_sql_query("SELECT participant, condition FROM participants", con)
    generation = pd.read_sql_query("SELECT * from generation", con)
    alphas = pd.read_sql_query("SELECT * from alphas", con)
    nppt = pd.read_sql_query("SELECT COUNT(*) from participants", con).values[0][0] #sample size
    #stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
    con.close()

    new_pid = range(nppt)
    random.shuffle(new_pid)
    # create categories mapping
    mapping = pd.DataFrame(columns = ['condition', 'categories'])
    for i in alphas.columns:
	As = alphas[i].as_matrix().flatten()
	mapping = mapping.append(
	    dict(condition = i, categories =[As]), 
	    ignore_index = True
	)


    # Prepare  category index
    catmaplist = [0,0,0,0,1,1,1,1]
    catmap = pd.DataFrame(catmaplist,columns = ['category'])
    stimcol = ['new_pid','participant','stimuli','category','condition']
    stimuli = pd.DataFrame(columns = stimcol)

    # Consolidate cat 1 stimuli
    for count,i in enumerate(participants['participant'].tolist()):
        stimtemp = pd.DataFrame(columns = stimcol)
        cat1 = generation['stimulus'].loc[generation['participant']==i]
        currcondition = participants['condition'].loc[participants['participant']==i].tolist()[0]
        cat0 = alphas[currcondition]        
        stim = cat0.append(cat1, ignore_index = True)        
        stimtemp['stimuli'] = stim
        stimtemp['category'] = catmap
        stimtemp['participant'] = i
        stimtemp['new_pid'] = new_pid[count]
        stimtemp['condition'] = currcondition
        stimuli = stimuli.append(stimtemp, ignore_index = True)

        # cat0list = generation['stimulus'].loc[generation['participant']==i].tolist()
        # currcondition = participants['condition'].loc[participants['participant']==i].tolist()
        # cat1list = mapping['categories'].loc[mapping['condition']==currcondition[0]]
        # cats = [cat0list,cat1list]
        # stimuli = stimuli. append(
            # dict(participant = i, categories = cats),
            # ignore_index = True
            # )

    # Get assignment information (specifically, the counterbalance index)
    con = sqlite3.connect(pref_ass + dbname)
    assignments = pd.read_sql_query("SELECT Participant, Counterbalance FROM Assignments",con)
    con.close()
    #rename relevant column for mapping
    assignments = assignments.rename(columns={'Participant':'participant'})

    # merge assignments to stimuli
    stimuli = pd.merge(stimuli, assignments, on='participant')

    # Sort by new_pid
    stimuli = stimuli.sort_values(by=['new_pid','category'], ascending=[True,True])
    
    # Rename some columns
    stimuli = stimuli.rename(columns = {'Counterbalance':'counterbalance'})
    stimuli = stimuli.rename(columns = {'participant':'old_pid'})

    con = sqlite3.connect(pref_out + dbname)
    stimuli.to_sql('stimuli',   con, index = False, if_exists = 'replace')
    con.close()


