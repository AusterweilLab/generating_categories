# Extract the pickled output that is produced from
# individual_model_gridsearch_CHTC.py and saves the best params as a pickle

import pickle, os, re, tarfile
import pandas as pd
import numpy as np
import time
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13


tardir = 'chtctar/'
privdir = os.path.join(tardir,'private') #private working folder that git ignores
if not os.path.isdir(privdir):
    os.system('mkdir {}'.format(privdir))
maintarname = 'allpickles_ind190618.tar.gz'
appendkey = ['finalparmsll','chunkstartparms','parmnames']
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
    checkre = re.match('pickles(\d\d*)_ind\.tar\.gz',maintarmember.name)
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
            checkmembername = re.search('chtc_ind_gs_best_params_(.*)_chunk{}\.p'.format(chunk),member.name)            
            if checkmembername != None:
                f = tar.extractfile(member)
                dataset = checkmembername.group(1)
                if not dataset in datasetsAll:
                    datasetsAll += [dataset]
                datachunk = pickle.load(f)
                models = datachunk.keys()
                #Remove fit_weights from models, since it's not a model
                fit_weights = False
                if 'fit_weights' in models:                                        
                    models.remove('fit_weights')
                    fit_weights = True
                if not dataset in data:
                    data[dataset] = dict()            
                for model in models:
                    if not model in modelsAll:
                        modelsAll += [model]
                    #Cycle through each participant and remove noninformative keys
                    nppt = len(datachunk[model])
                    ppts = datachunk[model].keys()
                    for ppt in ppts:
                        #Remove noninformative keys
                        for key in removekey:
                            datachunk[model][ppt].pop(key,None)
                        if not model in data[dataset]:
                            #If new model, copy over everythin
                            data[dataset][model] = dict()
                            data[dataset][model][ppt] = datachunk[model][ppt]
                        else:
                            #Otherwise, just append the stuff as ndicated by appendkey
                            if not ppt in data[dataset][model]:
                                data[dataset][model][ppt] = dict()
                                for key in appendkey:
                                    data[dataset][model][ppt][key] = datachunk[model][ppt][key]
                            else:
                                for key in appendkey:
                                    if not key in appendOnce:
                                        data[dataset][model][ppt][key] = np.concatenate((data[dataset][model][ppt][key], datachunk[model][ppt][key]),0)
        #Remove file from private folder after use
        os.system('rm {}'.format(os.path.join(privdir,filename)))
        
#Find best parms for each model in each dataset
pickledir = 'pickles/'
for dataset in datasetsAll:
    for model in modelsAll:
        if model in data[dataset].keys():
            ppts = data[dataset][model].keys()
            for ppt in ppts:
                results_all = data[dataset][model][ppt]['finalparmsll']
                ind = np.argsort(results_all[:,-2]) #-2 is the column containing of LL
                results_all_sorted = results_all[ind]
                results_best = results_all_sorted[0,:]
                #startp_sorted = data[dataset][model][ppt]['startparms'][ind]
                data[dataset][model][ppt]['finalparmsll'] = results_all_sorted
                #data[dataset][model][ppt]['startparms'] = startp_sorted
                data[dataset][model][ppt]['bestparmsll'] = results_best

                # f = tar.extractfile(member)
                # if f is not None:
                #     temp = pickle.load(f)
                #     content = f.read()
                #     lll
    # save final result in pickle    
    dst = dataset
    results = data[dataset]
    results['fit_weights'] = fit_weights
    with open('{}private/chtc_ind_gs_best_params_{}.p'.format(pickledir,dst),'wb') as f:
        #pass 
        pickle.dump(results, f)

