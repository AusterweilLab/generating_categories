execfile('Imports.py')

from Modules.Classes import Simulation
import re
import os
import pickle

#Find all gs fits and print them. Nice nice.        
pickledir = 'pickles/'
prefix = 'gs_'
#Compile regexp obj
allfiles =  os.listdir(pickledir)
r = re.compile(prefix)
gsfiles = filter(r.match,allfiles)

#Compute total SSE


for i,file in enumerate(gsfiles):
    #Extract key data from each file
    print '\n' + file
    print '------'
    with open(pickledir+file,'rb') as f:
        fulldata = pickle.load(f)
    modelnames = fulldata.keys()
    for j in modelnames:
        print 'Model:' + j
        for pi,pname in enumerate(fulldata[j]['parmnames']):
            print '\t' + pname + ': ' + str(fulldata[j]['bestparmsll'][pi])
        print '\tLogLike' + ' = ' + '-' + str(fulldata[j]['bestparmsll'][pi+1])
        print '\tAIC'  + ' = ' + str(fulldata[j]['bestparmsll'][pi+2])

