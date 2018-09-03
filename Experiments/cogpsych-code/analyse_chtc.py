# Extract the pickled output that is produced from
# global_model_gridsearch_CHTC.py

import pickle, os, re, tarfile, sys
import pandas as pd
import numpy as np
import time
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation


tardir = 'chtctar/'
privdir = os.path.join(tardir,'private') #private working folder that git ignores
if not os.path.isdir(privdir):
    os.system('mkdir {}'.format(privdir))

narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    maintarname = sys.argv[1]
else:
    maintarname = 'allpickles200818.tar.gz'
    
appendkey = ['finalparmsll','parmnames','chunkstartparms']
appendOnce = ['parmnames'] #append this key only once per participant
removekey = ['bestparmsll','chunkidx','startparms']
#Go through each tarball and find the chtc file
#allfiles = os.listdir(tardir)
data = dict()
datasetsAll = []
modelsAll = []
print_ct = 0
tarct = 0
maintar = tarfile.open(os.path.join(privdir,maintarname), "r:gz")
for maintarmember in maintar.getmembers(): #for checkfile in allfiles:
    checkre = re.match('pickles(\d\d*)\.tar\.gz',maintarmember.name)
    if checkre!=None:
        filename = checkre.group(0)
        chunk = checkre.group(1)
        #Print chunk currently processing
        print_ct = funcs.printProg(tarct,print_ct,steps = 20, breakline = 40)
        tarct += 1
        #extract file
        maintar.extract(maintarmember,privdir)
        tar = tarfile.open(os.path.join(privdir,filename), "r:gz")
        for member in tar.getmembers():            
            checkmembername = re.search('chtc_gs_best_params_(.*)_chunk{}\.p'.format(chunk),member.name)
            if checkmembername != None:
                f = tar.extractfile(member)
                dataset = checkmembername.group(1)
                #remove .p if in dataset - necessary for an annoying little bug in an earlier version of the fitting code
                dataset = dataset.replace('.p','')
                if not dataset in datasetsAll:
                    datasetsAll += [dataset]
                datachunk = pickle.load(f)
                models = datachunk.keys()
                if not dataset in data:
                    data[dataset] = dict()            
                for model in models:
                    if not model in modelsAll:
                        modelsAll += [model]
                    datachunk[model].keys                    
                    #Remove noninformative keys
                    for key in removekey:
                        datachunk[model].pop(key,None)
                    if not model in data[dataset]:
                        #If new model, copy over everythin
                        data[dataset][model] = datachunk[model]
                    else:
                        #Otherwise, just append the stuff as ndicated by appendkey
                        for key in appendkey:
                            if not key in appendOnce:
                                data[dataset][model][key] = np.concatenate((data[dataset][model][key], datachunk[model][key]),0)
        #Remove file from private folder after use
        os.system('rm {}'.format(os.path.join(privdir,filename)))
        
#Find best parms for each model in each dataset
pickledir = 'pickles/'
for dataset in datasetsAll:
    for model in modelsAll:
        results_all = data[dataset][model]['finalparmsll']
        ind = np.argsort(results_all[:,-2]) #-2 is the column containing of LL
        results_all_sorted = results_all[ind]
        results_best = results_all_sorted[0,:]
        #startp_sorted = data[dataset][model]['startparms'][ind]
        data[dataset][model]['finalparmsll'] = results_all_sorted
        #data[dataset][model]['startparms'] = startp_sorted
        data[dataset][model]['bestparmsll'] = results_best
                            
            # f = tar.extractfile(member)
            # if f is not None:
            #     temp = pickle.load(f)
            #     content = f.read()
            #     lll
    # save final result in pickle    
    dst = dataset
    results = data[dataset]
    with open('{}chtc_gs_best_params_{}.p'.format(pickledir,dst),'wb') as f:
        #pass 
        pickle.dump(results, f)

