execfile('Imports.py')

from Modules.Classes import Simulation
import Modules.Funcs as funcs
import re
import os
import pickle
import csv
import pandas as pd
import numpy as np

#Find all gs fits and print them. Nice nice.        
pickledir = 'pickles/private/'
writedir = 'indfits'
prefix = 'chtc_ind_gs_best_params'
#Compile regexp obj
allfiles =  os.listdir(pickledir)
r = re.compile(prefix)
gsfiles = filter(r.match,allfiles)

#Compute total SSE
headerBase = ['ppt','nLL','AIC'] #First line of csv - add data_names to this
data_names = []
results = [] #This will be same length as data_names
for i,file in enumerate(gsfiles):
    #Extract key data from each file    
    # print '\n' + file
    # print '------'
    data_name = gsfiles[0][len(prefix)+1:-2] #ignore the prefix when populating data names
    data_names += [data_name]
    with open(pickledir+file,'rb') as f:
        fulldata = pickle.load(f)        
    model_names = fulldata.keys()    
    for j in model_names:
        # Extract parameter names and add to header
        header = headerBase[:]
        nparms = 0
        modelname_print = funcs.getModelName(j,fetch='short') #fetch short version of model name
        for pi,pname in enumerate(fulldata[j][0]['parmnames']):
            header += [pname]
            nparms += 1
        #with open(os.path.join(writedir,file[0:len(file)-2]+'_'+modelname_print+'.csv'),'wb') as f:
        with open(os.path.join(writedir,modelname_print+'.csv'),'wb') as f:            
            wr = csv.writer(f)
            #write header
            wr.writerow(header)
            for ppt in fulldata[j].keys():
                reorder = np.concatenate(([nparms,nparms+1],range(nparms)))  #bring nll and AIC to the front
                pptdata = fulldata[j][ppt]['bestparmsll'][reorder]
                pptdata = list(pptdata) #things seem a little simpler as lists
                pptdata = [int(ppt)] + pptdata #force ppt to be integer so it prints nicely in csv
                #pptdata = np.concatenate(([ppt],pptdata))                
                wr.writerow(pptdata)


