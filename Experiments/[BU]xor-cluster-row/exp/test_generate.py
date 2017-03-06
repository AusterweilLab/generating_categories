print '\nRUNNING GENERATION TEST..........'
phase='generate'

##--------------------------------------------------------
bothscales, poses = [], [[-220,200],[-220,0]]
for i in range(len(stimulusspace)):
    bothscales.append( visual.RatingScale(win, 
        low = 0, high = stimulusspace[i]-1,
        labels=featurelabels[i], scale = None, showAccept = False, 
        leftKeys=None,rightKeys=None,skipKeys=None,respKeys=None,
        textColor=txtcolor,  textFont=txtfont, textSize=.7, 
        stretch = 0.8, marker = 'triangle', markerColor = 'black',
        lineColor=[-1,-1,-1], showValue = False, pos=poses[i]) 
        )


# relocate stimuli
imagepos = [220, 100]
for i in [OKbutton, OKlabel]:
    i.setPos((0, -200))

completed_exemplars = []
already_complete = visual.TextStim(win,text='You have already created this example!',
    height=txtsize,font=txtfont,color=txtcolor,wrapWidth=900,alignVert='center',
    alignHoriz='center', pos=imagepos)

##--------------------------------------------------------
## BEGIN ITERATING OVER BLOCKS AND TRIALS
presentinstructions(win,instructions,instructiontext,phase)
for trialnumber in range(len(trainingitems)):
    
    #get instructions
    string='Use the scales to create an example.'
    instructions.setText(string) 
    instructions.pos = (0,-120) 

    # reset scales, clear events
    [i.reset() for i in bothscales]
    event.clearEvents()

    #draw instructions, buttons, and image
    drawall(win,[instructions,bothscales])
    
    #wait for response
    timer.reset()
    while not cursor.isPressedIn(OKbutton):        

        # quit if desired
        if 'q' in event.getKeys(keyList='q'):
            print 'USER TERMIMATED'
            cursor.win.close()
            core.quit()

        # read scales, generate exemplar if values are provided
        bothratings = [j.getRating() for j in bothscales]

        if all(isinstance(j, int) for j in bothratings):
            newcoords = [possiblevalues[j][bothratings[j]] for j in range(len(bothratings))]
            newcoords = tuple(newcoords)

            if not newcoords in completed_exemplars:
                stimulus = [ i[0] for i in grid_stimuli if i[2]==newcoords][0]
                stimulus.setPos(imagepos)
                drawall(win,[instructions,bothscales,OKbutton,OKlabel,stimulus])
            else:
                drawall(win,[instructions,bothscales,already_complete])

        else:
            drawall(win,[instructions,bothscales])
            

    rt = timer.getTime()
    drawall(win,[stimulus])
    core.wait(.5)

    # get final item info
    finalcoords = [possiblevalues[j][bothratings[j]] for j in range(len(bothratings))]
    finalcoords = tuple(finalcoords)
    finalnumber = [ i[1] for i in grid_stimuli if i[2]==finalcoords]
    
    # add final exemplar to completed list
    completed_exemplars.append(finalcoords)

    # PRINTING...
    print '\nGeneration Trial '+str(trialnumber)+' information:'
    print ['Final Stimulus: ', finalnumber, 'Features: ', finalcoords]
    print ['RT: ', rt]
    
    #log data
    trialdata=[condition,subjectid,phase,'',trialnumber,finalnumber,finalcoords,rt]
    subjectdata.append(trialdata)
    writefile(subjectfile,subjectdata,',')

