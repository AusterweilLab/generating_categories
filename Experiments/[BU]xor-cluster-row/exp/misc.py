from psychopy import event, core, gui
import numpy as np
from socket import gethostname
from operator import mul
from itertools import permutations
import os, shutil
from os.path import join as pj

#-------------------------------------------------------------------------------
# creates folder if it doesnt exist
def checkdirectory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
#-------------------------------------------------------------------------------
# copies the data file to a series of dropbox folders
def copy2db(filename,experimentname):
    copyfolders=[ #add your own!
        'C:\\Users\\klab\\Dropbox\\PSYCHOPY DATA\\'+experimentname+'\\',
        'C:\\Users\\klab\\Dropbox\\nolan\\PSYCHOPY DATA\\'+experimentname+'\\']

    for i in copyfolders:
        checkdirectory(i)
        shutil.copy(filename,i)

#-------------------------------------------------------------------------------
# flatten an arbitrarily nested list
def flatten(LIST):
    for i in LIST:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i

#-------------------------------------------------------------------------------
# write a list to a file, where each item gets its own line,
# independently of nesting and data type
def writefile(filename,data,delim):
    lines = [] # open storage

    # iterate across lines
    for line in data:

        # recursive flatten until there are no more lists
        if isinstance(line, (list, tuple)):
            lines.append(delim.join(str(i) for i in flatten(line)))

        # add item to list if not a list/tuple
        else:
            lines.append(str(line))

    # write joined lines to file
    fh=open(filename,'w')
    fh.write("\n".join(lines))
    fh.close() 


#-------------------------------------------------------------------------------
# do a dialouge and return subject info 
def getsubjectinfo(exptitle,conditions,subjectfolder):

    
    myDlg = gui.Dlg(title=exptitle)
    myDlg.addText('Subject Info')
    myDlg.addField('ID:', tip='or subject code')
    myDlg.addField('Condition:', choices=conditions)
    myDlg.show()
    if not myDlg.OK:
        core.quit()

    subjectinfo = [str(i) for i in myDlg.data]

    if subjectinfo[0]=='':
        print 'USER TERMIMATED'
        core.quit()
    else: 
        subjectid=subjectinfo[0]
        condition=subjectinfo[1]
        subjectfile = pj(subjectfolder,exptitle+'-'+subjectid+'-'+condition+'.csv')
        while os.path.exists(subjectfile) == True:
            subjectfile+='_dupe'
        return [int(subjectid),int(condition),subjectfile]

#-------------------------------------------------------------------------------    
#takes in lists of objects and draws them in the window. 
# objects may be arbitrarily nested
def drawall(win,objects):
    for i in objects:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                j.draw()
        else:
            i.draw()
    win.flip()
#-------------------------------------------------------------------------------
# takes in stim and labels and returns a list of all possible combinations
def makecombos(a,b):
    return [[i,j] for i in a for j in b]

#-------------------------------------------------------------------------------
def number2Features(number,dimensions):
    # create a full, labeled example space
    totaln=reduce(mul, dimensions)
    space=np.array(range(0,totaln))+1
    space=space.reshape(dimensions)
    
    #look up the example number
    coordinates = np.where(space==number)
    coordinates = [int(i)+1 for i in list(coordinates)]
    return coordinates

#-------------------------------------------------------------------------------
def starttrial(win,isi,fixcross):
    fixcross.draw()
    win.flip()
    core.wait(isi)

#-------------------------------------------------------------------------------   
def presentinstructions(win,stim,text,phase):
    event.clearEvents()
    stim.pos = (0.0,0.0)
    stim.alignVert = 'center'

    #search text for instructions matching phase
    for i in text:
        if i[0]==phase:
            instructs=i[1]
            break

    #draw text and wait for key press
    stim.setText(instructs)
    stim.draw()
    win.flip()
    core.wait(2)

    if 'q' in event.waitKeys(keyList=['q','space']):
        print 'USER TERMIMATED'
        win.close()
        core.quit()
    
    event.clearEvents() 

#-----------------------------------------------------------------------------------
## waits for mouse to select a visual object. returns a corresponding label
def waitforresponse(cursor,timer,buttons,labels):

    #clear events
    timer.reset()
    cursor.clickReset()
    event.clearEvents() 

    #iterate until response
    while True:

        #quit if desired
        if 'q' in event.getKeys(keyList='q'):
            print 'USER TERMIMATED'
            cursor.win.close()
            core.quit()

        #check to see if  any stimulus has been clicked inside of
        for i in buttons:
            if cursor.isPressedIn(i):
                return [labels[buttons.index(i)],timer.getTime()]

#-----------------------------------------------------------------------------------
## program waits for a mouse click to continue
def clicktocontinue(cursor):
    event.clearEvents()
    cursor.clickReset()
    while not any(cursor.getPressed()):
        if event.getKeys(keyList='q'):
            print 'USER TERMIMATED'
            cursor.win.close()
            core.quit()

#-----------------------------------------------------------------------------------
## prints each item in a list on a new line
def printlist(toprint):
    for i in toprint:
        print i

#-----------------------------------------------------------------------------------
## get unique items in a list
def uniqify(seq, idfun=None): 
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


#-----------------------------------------------------------------------------------
## returns all counterbalance info for the subject ID provided
def getcounterbalance(dimensions,balancecondition):
    ndims=len(dimensions)

    # get all permutations of feature order and flipping
    featureorder=list(permutations(range(ndims)))
    featureflip=np.eye(ndims+1)[:,1:].astype(int).tolist()
    allconditions=makecombos(featureflip,featureorder)

    # get balance condition info for the subject
    [flipdims,assigndims]=allconditions[balancecondition]
    assigndims=list(assigndims)

    # create a stimulus space
    totaln=reduce(mul, dimensions)
    space=np.array(range(0,totaln))+1
    space=space.reshape(dimensions)

    ##flip dimensions
    k=0
    for dim in flipdims:
        if dim==1:
            space = np.swapaxes(
                np.swapaxes(space, 0, k)[::-1], 0, k)
        k+=1

    ##reorder dimensions
    space=np.transpose(space,axes=assigndims)

    # convert space back into a vector list
    reassignments=np.ravel(space)
    reassignments=reassignments.tolist()
    return [reassignments, flipdims, assigndims]

