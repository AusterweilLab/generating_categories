from psychopy import visual, event, core
import os, sys
import numpy as np
from misc import *
from socket import gethostname
from operator import itemgetter
from time import strftime
from os.path import join as pj
import itertools as it
execfile('instructions.py')


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#-----------GET EXPERIMENT INFO------------
experimentname = os.path.split(os.path.split(__file__)[0])[-1]
conditions = [1,2,3,4]
isi, numtrainingblocks = 0.5, 3
txtcolor, txtfont, txtsize = [-1,-1,-1], 'Consolas', 22

# set up stimulus grid on physical values
featureorder, stimulusspace = ['Size','Color'], [9,9]
sizevalues  = np.linspace(  75, 200, num = stimulusspace[0])
shadevalues = np.linspace(-0.8, 0.8, num = stimulusspace[1])
possiblevalues = [sizevalues,shadevalues]
coordinates = np.array(list(it.product(sizevalues,shadevalues)))
featurelabels = [
		['Smaller','Bigger'],
		['Darker','Lighter']
		]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##Specify directories
subjectsfolder       = pj(os.getcwd(), 'subjects')
logdir               = pj(os.getcwd(), 'logfiles')
    
## get subject information
checkdirectory(subjectsfolder)
[subjectid,condition,subjectfile] = getsubjectinfo(
    experimentname,conditions,subjectsfolder)
# subjectid,condition,subjectfile = 1,1, pj(os.getcwd(), 'subjects','DEMO-1-1.csv')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# CREATE WINDOW AND SET LOGGING OPTIONS
if gethostname() not in ['klab1','klab2','klab3']:
    win=visual.Window([1440,900],units='pix',color=[1,1,1])
else:
    win=visual.Window(fullscr=True,units='pix',color=[1,1,1])
    checkdirectory(logdir)
    logfile = pj(logdir, str(subjectid) + '-logfile.txt')
    while os.path.exists(logfile):
        logfile+='_dupe.txt'
    logfile=open(logfile,'w')
    sys.stdout, sys.stderr = logfile, logfile

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# GET COUNTERBALANCE INFO, PRINT TO LOG.

##determine counterbalance information
balancecondition=np.random.choice(5+1)
balanceinfo=getcounterbalance(stimulusspace,balancecondition)
[imageassignments, flipdims, assigndims] = balanceinfo

# adjust feature strings for counterbalance
featureorder=[ featureorder[i] for i in assigndims]
featurelabels = [ featurelabels[i] for i in assigndims]
[featurelabels[i].reverse() for i in range(len(featurelabels)) if flipdims[i]]

# adjust dimension values for counterbalance
possiblevalues = [ possiblevalues[i] for i in assigndims]
for i in range(len(possiblevalues)):
		if flipdims[i]:
			possiblevalues[i] = possiblevalues[i][::-1]
stimulusspace=[ stimulusspace[i] for i in assigndims]
coordinates = coordinates[:,assigndims]

##get current date and time
starttime=strftime("%d %b %Y %X")

# get running computer
pc=gethostname()

print '\n SUBJECT INFORMATION:'
print ['Start Time: ', starttime]
print ['PC: ', pc]
print ['ID: ', subjectid]
print ['Condition: ', condition]
print ['Counterbalance condition', balancecondition]
print ['Flipped Dimensions', flipdims]
print ['Feature Order',featureorder]
print ['File: ',subjectfile]

# initalize a data list                    
subjectdata=[	[starttime],
				[pc,subjectid,condition],
				[balancecondition,featurelabels]
			]
# --------SET UP THE INITAL CATEGORY
# ----------------------------------
#  200px  73 74 75 76 77 78 79 80 81
#    |    64 65 66 67 68 69 70 71 72
#    |    55 56 57 58 59 60 61 62 63
#  SIDE   46 47 48 49 50 51 52 53 54
# LENGTH  37 38 39 40 41 42 43 44 45
#    |    28 29 30 31 32 33 34 35 36
#    |    19 20 21 22 23 24 25 26 27
#    |    10 11 12 13 14 15 16 17 18
#  75px   1  2  3  4  5  6  7  8  9
#         0.1-------COLOR--------0.9
# ----------------------------------

if condition==1:
	trainingitems = [ 1, 11, 71, 81] # half XOR
elif condition==2:
	trainingitems = [ 7, 9, 25, 27] # cluster
elif condition==3:
	trainingitems = [2, 4, 6, 8] # row
elif condition==4:
	trainingitems = [38, 48, 58, 68] # diagonal


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# -------GENERATE EXPERIMENT STIMULI----------
grid_stimuli, n = [], 1
for num in imageassignments:
	if featureorder[0]=='Size':
		size, shade = coordinates[num-1]
	else:
		shade, size = coordinates[num-1]
	grid_stimuli.append([
		visual.Rect(win, width = size, height = size, units = 'pix',
			fillColor = (shade,shade,shade), fillColorSpace = 'rgb',
			lineColor = 'black', lineWidth = 1.0), n, tuple(coordinates[num-1])])
	n+=1

print '\n-------------------- GRID STIMULI --------------------'
printlist(grid_stimuli)

# make instruction stimuli
instructions=visual.TextStim(win,text='',height=txtsize,font=txtfont,
     color=txtcolor,wrapWidth=900,alignVert='center',alignHoriz='center',
     pos=[0.0,0.0])
fixcross=visual.TextStim(win,text='+',
     height=txtsize,font=txtfont,color=txtcolor,pos=(0,150))


##create an OK button
OKbutton = visual.Rect(win, width=75, height=50, units = 'pix',
        fillColor = 'white', lineColor = 'black', lineWidth=2.0, pos = (0, -110))
OKlabel  = visual.TextStim(win, text = 'OK', pos=OKbutton.pos,
        height=txtsize,font=txtfont, color=txtcolor)


continuestring='\n\
\n\
Click anywhere to continue.'
cursor = event.Mouse(visible=True, newPos=None, win=win)
timer=core.Clock() #clock


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# PASS TO PHASE SCRIPTS
execfile('train_observe.py')
execfile('test_generate.py')
execfile('test_generalize.py')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# TERMINATE EXPERIMENT
finishtime=strftime("%a, %d %b %Y %X")
print '\nStart Time: ' +starttime
print 'End Time: ' +finishtime +'\n'
subjectdata[0].append(finishtime)
writefile(subjectfile,subjectdata,',')

#do exit screen
instructions.setText(instructiontext[-1][-1])
instructions.pos=[0.0,0.0]
instructions.alignVert='center'
instructions.draw(win)
win.flip()
event.waitKeys()

print '\nExperiment complete.'
win.close()
if gethostname() in ['klab1','klab2','klab3']:
    copy2db(subjectfile,experimentname)
    logfile.close()
    os.system("TASKKILL /F /IM pythonw.exe")
