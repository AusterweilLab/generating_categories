print '\nRUNNING OBSERVATION TRAINING..........'
phase='training'

##--------------------------------------------------------
##define training block
trainingblock=[list(j) for i in trainingitems for j in grid_stimuli if i==j[1]]

print '\n -----TRAINING BLOCK'
printlist(trainingblock)
## BEGIN ITERATING OVER BLOCKS AND TRIALS
execfile('start_instructs.py')
for block in range(1,numtrainingblocks+1):
    np.random.shuffle(trainingblock)
    trialnumber=0
    for trial in trainingblock:
        starttrial(win,isi,fixcross)
        
        #get instructions
        string='This a a member of the Alpha category.  '
        instructions.setText(string)
        
        # define critical items
        trialnumber += 1
        stimulus, stimnumber, stimcoords = trial

        stimulus.setPos((0, 150))

        #draw instructions, buttons, and image
        drawall(win,[stimulus,instructions])
        core.wait(1)
        drawall(win,[OKbutton,OKlabel,stimulus,instructions])
        
        #wait for response
        timer.reset()
        while not cursor.isPressedIn(OKbutton):

            # quit if desired
            if 'q' in event.getKeys(keyList='q'):
                print 'USER TERMIMATED'
                cursor.win.close()
                core.quit()

        rt = timer.getTime()
        drawall(win,[stimulus])
        core.wait(.5)
        


        # PRINTING...
        print '\nTraining Block '+str(block)+', Trial '+str(trialnumber)+' information:'
        print ['Image ID: ', stimnumber]
        print ['coordinates: ',stimcoords]
        print ['RT: ', rt]
        
        #log data
        trialdata=[condition,subjectid,phase,block,trialnumber,
            stimnumber,stimcoords,rt]
        subjectdata.append(trialdata)
        writefile(subjectfile,subjectdata,',')

