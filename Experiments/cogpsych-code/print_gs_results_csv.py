execfile('Imports.py')

from Modules.Classes import Simulation
import re
import os
import pickle
import pandas as pd

#Find all gs fits and print them. Nice nice.        
pickledir = 'pickles/'
prefix = 'chtc_gs_best_params'
#Compile regexp obj
allfiles =  os.listdir(pickledir)
r = re.compile(prefix)
gsfiles = filter(r.match,allfiles)

#Compute total SSE
header = ['Model','Parameters'] #First line of csv - add data_names to this
data_names = []
results = [] #This will be same length as data_names
for i,file in enumerate(gsfiles):
    #Extract key data from each file    
    # print '\n' + file
    # print '------'
    data_names += [gsfiles[0][len(prefix)+1:-2]] #ignore the prefix when populating data names    
    with open(pickledir+file,'rb') as f:
        fulldata = pickle.load(f)        
    model_names = fulldata.keys()
    for j in model_names:
        # print j
        for pi,pname in enumerate(fulldata[j]['parmnames']):
            print '\t' + pname + ': ' + str(fulldata[j]['bestparmsll'][pi])
        print '\tLogLike' + ' = ' + '-' + str(fulldata[j]['bestparmsll'][pi+1])
        print '\tAIC'  + ' = ' + str(fulldata[j]['bestparmsll'][pi+2]) + '\n'

