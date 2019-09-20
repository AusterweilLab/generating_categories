execfile('Imports.py')

from Modules.Classes import Simulation
import Modules.Funcs as funcs
import re
import os
import pickle
import pandas as pd
import csv
import numpy as np
#Find all gs fits and print them. Nice nice.        
pickledir = 'pickles/'
writefile = 'globalfits'
prefix = 'chtc_gs_best_params'
printdata = ['xcr']#['5con','corner','all']#'all'
if not printdata is 'all':
    gsfiles = []
    data_names = []
    allfiles =  os.listdir(pickledir)
    for i in printdata:
        pattern = '{}_(.*{}.*).p'.format(prefix,i)
        gsfiles += [re.match(pattern,file).group(0) for file in allfiles if re.match(pattern,file)]
        data_names += [re.match(pattern,file).group(1) for file in allfiles if re.match(pattern,file)]
else:
    allfiles =  os.listdir(pickledir)
    r = re.compile(prefix)
    pattern = '{}_(.*).p'.format(prefix)
    gsfiles = [re.match(pattern,file).group(0) for file in allfiles if re.match(pattern,file)]
    data_names = [re.match(pattern,file).group(1) for file in allfiles if re.match(pattern,file)]
    #r = re.compile('{}_({}.*)'.format(prefix,printdata))
    #gsfiles = filter(r.match,allfiles)


headerBase = ['Model','Parm'] #First line of csv
results = [] #This will be same length as data_names
# Extract datafile names  and add to header
header = headerBase[:]

for dname in data_names:
    header += [dname]

#Iterate though each data file
data = dict()
parmnames_global = {}
for i,file in enumerate(gsfiles):
    with open(pickledir+file,'rb') as f:
        fulldata = pickle.load(f)        
    model_names = fulldata.keys()
    dn = data_names[i]
    #Iterate through each model
    for mn in model_names:
        #with open(os.path.join(writedir,file[0:len(file)-2]+'_'+modelname_print+'.csv'),'wb') as f:
        parmnames = fulldata[mn]['parmnames']
        parmnames_global[mn] = parmnames
        nparms = len(parmnames)
        nllAIC = fulldata[mn]['bestparmsll'][[nparms,nparms+1]]
        parmvals = fulldata[mn]['bestparmsll']
        for pi,parm in enumerate(parmnames):
            if not mn in data.keys():
                data[mn] = dict()
            if not dn in data[mn].keys():
                data[mn][dn] = dict()
            data[mn][dn]['nllAIC'] = nllAIC
            data[mn][dn][parm] = parmvals[pi]

#Perform the writing separately to make things a bit neater
with open(writefile+'.csv','wb') as f:
    wr = csv.writer(f)
    #write header
    wr.writerow(header)
    model_names = data.keys()
    for mn in model_names:
        model_print = funcs.getModelName(mn,fetch='short') #fetch short version of model name
        parmnames = parmnames_global[mn]
        for parm in parmnames:
            parmvals = []
            for dn in data_names:
                if dn in data[mn].keys():
                    parmvals += ['{:.3f}'.format(round(data[mn][dn][parm],3))]
                else:
                    parmvals += [' ']
                    
            data_write = np.concatenate([[model_print],[parm],parmvals])
            data_write = list(data_write) #things seem a little simpler as lists
            #print(data_write)
            wr.writerow(data_write)
        #Write nll and AIC
        nll = []
        for dn in data_names:
            if dn in data[mn].keys():
                nll += ['{:.3f}'.format(round(data[mn][dn]['nllAIC'][0],3))]
            else:
                nll += [' ']
        data_write = np.concatenate([[model_print],['nLL'],nll])
        data_write = list(data_write) #things seem a little simpler as lists
        wr.writerow(data_write)
        aic = []
        for dn in data_names:
            if dn in data[mn].keys():
                aic += ['{:.3f}'.format(round(data[mn][dn]['nllAIC'][1],3))]
            else:
                aic += [' ']
                
        data_write = np.concatenate([[model_print],['AIC'],aic])
        data_write = list(data_write) #things seem a little simpler as lists
        wr.writerow(data_write)


