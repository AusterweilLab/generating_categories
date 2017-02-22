print '\nRUNNING GENERALIZATION TEST..........'
phase='generalization'

##--------------------------------------------------------
generalization = list(grid_stimuli)
response_options = ['Alpha','Beta']

# set up image positions
for i in generalization:
    i[0].pos = (0, 150)

# make A / Not A buttons
buttonstim, buttontext = [], []
for i in response_options:
    buttonstim.append(
        visual.Rect(win, width=75, height=50, units = 'pix',
            fillColor = 'white', lineColor = 'black', lineWidth=2.0, 
            pos = (-150, -110))
        )

    if i==response_options[1]:
        buttonstim[-1].pos[0] *= -1

    buttontext.append(
        visual.TextStim(win, text = i, pos=buttonstim[-1].pos,
            height=txtsize,font=txtfont, color=txtcolor)
        )


## BEGIN ITERATING OVER BLOCKS AND TRIALS
presentinstructions(win,instructions,instructiontext,phase)
np.random.shuffle(generalization)
trialnumber=0
for trial in generalization:
    starttrial(win,isi,fixcross)
    
    #get instructions
    string='Click a button to select the correct category.'
    instructions.setText(string)
    
    # define critical items
    trialnumber += 1
    stimulus = trial[0]
    imagenumber = trial[1]
    coordinates = trial[2]
    
    #draw instructions, buttons, and image
    drawall(win,[stimulus])
    core.wait(.5)
    drawall(win,[buttonstim,buttontext,stimulus,instructions])
    # core.wait(.5)
    
    #wait for response
    [response,rt]=waitforresponse(cursor,timer,buttonstim,response_options)
    drawall(win,[stimulus])     
    core.wait(.5)


    # PRINTING...
    print '\nGeneralization Trial '+str(trialnumber)+' information:'
    print ['Image ID: ', imagenumber]
    print ['Response: ', response]
    
    #log data
    trialdata=[condition,subjectid,phase,trialnumber,imagenumber,
        coordinates,response,rt]
    subjectdata.append(trialdata)
    writefile(subjectfile,subjectdata,',')

