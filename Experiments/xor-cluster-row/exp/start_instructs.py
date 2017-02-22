# special startup instructions

samples = [grid_stimuli[i-1][0] for i in [1, 17 , 65, 81]]
locations = [   [-355,75],
                [-125,75],
                [105,75],
                [335,75],
        ]
for i in samples:
    i.pos = locations[samples.index(i)]

line1 = 'In this experiment, you will observe geometric figures like the ones below:'

line2 = 'We will show you some examples like these, all belonging to a common category called "Alpha".  Examples of the Alpha category will appear one at a time, and your job is to learn as much as you can about the category.  Afterwards, we will ask you a series of questions about what you have learned.\n\nPress the spacebar when you are ready to continue.'


txt = line1+'\n\n\n\n\n\n\n\n\n\n\n\n\n'+line2


event.clearEvents()
instructions.pos = (0.0,0.0)
instructions.alignVert = 'center'
instructions.setText(txt)
drawall(win,[instructions,samples])
core.wait(2)

# check if user quit or advanced
if 'q' in event.waitKeys(keyList=['q','space']):
    print 'USER TERMIMATED'
    win.close()
    core.quit()
event.clearEvents() 

instructions.alignVert = 'top'


