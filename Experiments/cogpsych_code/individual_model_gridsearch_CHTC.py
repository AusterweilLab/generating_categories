import pickle, sys, os
import pandas as pd
import numpy as np
import time
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13

#Toggle 
fit_weights = False
fiterror = False #Toggle if fitting error (as opposed to category choices)

# Specify defaults
#dataname_def = 'catassign'

WT_THETA = 1.5 #for the attention weight fitting
datasets = ['catassign']#why are fits to this so slow? 110518 ok fixed!
participant_def = 'all'
unique_trials_def = 'all'
nchunks = 1000 #number of CHTC instances to run
#Allow for input arguments at the shell
narg = len(sys.argv)

if __name__ == "__main__" and narg>1:
    # if len(sys.argv)<4:
    #         unique_trials = unique_trials_def
    # else:
    #         unique_trials = int(sys.argv[3])
    # if len(sys.argv)<3:
    #         participant = participant_def
    # else:
    #         participant = int(sys.argv[2])
    # if len(sys.argv)<2:
    #         dataname = dataname_def
    # else:
    #         dataname = sys.argv[1]
    #dataname = dataname_def
    participant = participant_def
    unique_trials = unique_trials_def
    runchunk = int(sys.argv[1]) #first arg from terminal is chunk idx
else:
    #dataname = dataname_def
    participant = participant_def
    unique_trials = unique_trials_def
    runchunk = 1;
#datasets = ['pooled','pooled-no1st','xcr','midbot','catassign','nosofsky1986','nosofsky1989','NGPMG1994']        


#Check that output directory exists, otherwise create it
pickledir = 'pickles/'
outputdir = pickledir + 'newpickles/'
if not os.path.isdir(outputdir):
    os.system('mkdir ' + outputdir)


    
for dataname in datasets:
    execfile('validate_data.py')
        
    print 'Grid Searching Data: ' + dataname
    
    # get data from pickle
    with open(pickledir+src, "rb" ) as f:
        trials = pickle.load( f )

    if fiterror:
        #Force task to fit error, and appen err to dst filename
        trials.task = 'error'
        dst = dst[0:-2] + '_fit2error' + dst[-2:]
    else:
        trials.task = task

    #add chunk number to dst
    dst = dst[0:-2] + '_chunk' + str(runchunk) + '.p'
    dst_error = dst[0:-2] + '_error.p'


    #Get generation data for computation of individual weights,
    # if applicable
    if len(raw_db)>0 and fit_weights:
        con = sqlite3.connect(raw_db)
        stats = pd.read_sql_query("SELECT * from betastats", con)
        con.close()
    
    #print trials
    trials = Simulation.extractPptData(trials,participant,unique_trials)
    

    # options for the optimization routine
    options = dict(
        method = 'Nelder-Mead',
        options = dict(maxiter = 500, disp = False),
        tol = 0.01,
    ) 


    #Run grid search
    results = dict()
    results['fit_weights'] = fit_weights
    for model_obj in [Packer, CopyTweak, ConjugateJK13, RepresentJK13]:
        #Prepare list of grid search start points
        #Create base array
        nparms = len(model_obj.parameter_names)
        steps = 5
        stepsize = float(1)/steps
        startp_base = funcs.ndspace(steps+1,nparms,0,1)
        #Set some defaults
        mindef = -6
        maxdef = 6 #follows uniform distribution if using rvs
        #Adjust the scale of the array so the min and max values of parms aren't included
        adjustrangemin = stepsize
        adjustrangemax = 1-stepsize
        adjustrange = adjustrangemax-adjustrangemin
        startp = startp_base*adjustrange+adjustrangemin
        #extract only relevant chunk from startp
        nfitsTotal = startp.shape[0]
        chunkSize = np.floor(float(nfitsTotal)/nchunks)
        chunkRemain = np.mod(float(nfitsTotal),nchunks) #remaining fits to be split over chunks
        #Distribute remaining fits over the first-chunkremain number of chunks
        if runchunk<chunkRemain:
            chunkSize += 1        
            chunkIdxStart = runchunk*(chunkSize)
            chunkIdxEnd = chunkIdxStart+chunkSize
        else:
            chunkRemainMax = chunkRemain * (chunkSize+1)
            chunkIdxStart = chunkRemainMax + (runchunk-chunkRemain)*(chunkSize)
            chunkIdxEnd = chunkIdxStart+chunkSize        
        
        chunkIdxStart = int(chunkIdxStart)
        chunkIdxEnd = int(chunkIdxEnd)
        startp = startp[chunkIdxStart:chunkIdxEnd,:]
        
        #Adjust min and max of starting parameters
        for pname,prule in model_obj.parameter_rules.items():
            idx = model_obj.parameter_names.index(pname)
            if 'max' in prule:
                max = prule['max']
            else:
                max = maxdef
                
            startp[:,idx] = startp[:,idx] * max
        
            if 'min' in prule:
                min = prule['min']
            else:
                min = mindef
                
            startp[:,idx] = startp[:,idx] + min
        
        nfits = startp.shape[0]
        print 'Fitting: ' + model_obj.model
        print 'Total possible starting points: {}'.format(nfitsTotal)
        print 'Running chunk {}, extracting starting points: [{}:{}]'.format(runchunk, chunkIdxStart, chunkIdxEnd)
        print 'Total starting points extracted: ' + str(nfits)
        printcol = 20
        if nfits==0:
            print 'No starting points extracted, moving on.\n'
            continue
        print 'Fitting participants:'
        #Run this for each participant, get the fits
        results[model_obj.model] = dict()        
        print_ct = 0
        for ppt in trials.participants:
            ppt = int(ppt)
            
            print_ct = funcs.printProg(ppt,print_ct,steps = 1, breakline = 20, breakby = 'char')

            # if np.mod(ppt+1,printcol) != 0:
            #     print str(ppt),
            #     sys.stdout.flush()
            # else:
            #     print str(ppt)

            results_array = np.array(np.zeros([nfits,nparms+2])) #nparms+2 cols, where +2 is the LL and AIC. Third dimension is for each individual participant
            results_model = dict()
            trials_ppt = Simulation.extractPptData(trials,ppt)
            pptOld = funcs.getCatassignID(ppt,source='analysis',fetch='old')
            fixedparams = dict()
            if fit_weights:
                #Apply weights
                ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
                fixedparams['wts'] = funcs.softmax(-ranges, theta = WT_THETA)[0]
                if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
                    fixedparams['wts'] = 1.0 - fixedparams['wts']

            for i in range(nfits):                
                inits = startp[i,:]
                res = Simulation.hillclimber(model_obj, trials_ppt, options,
                                             inits=inits, fixedparams = fixedparams,
                                             results = False, callbackstyle='none')
                final_parms = res.x
                final_ll = res.fun
                final_aic =  funcs.aic(final_ll,nparms)
                final_results_row = np.array(final_parms + [final_ll] + [final_aic]) #np.append(final_parms,final_ll)
                results_array[i,:] = final_results_row


            #Get indices sorted to LL
            ind = np.argsort( results_array[:,-2] );
            startp_sorted = startp[ind]
            results_array_sorted = results_array[ind]
            results_best = results_array_sorted[0,:]
            results_model['startparms'] = startp_sorted
            results_model['finalparmsll'] = results_array_sorted
            results_model['bestparmsll'] = results_best
            results_model['parmnames'] = model_obj.parameter_names
            #Also include chunk details
            results_model['chunkidx'] = [chunkIdxStart,chunkIdxEnd]
            results_model['chunkstartparms'] = startp

            results[model_obj.model][ppt] = results_model
            
            #X = model_obj.params2dict(model_obj.clipper(res.x))
            #results[model_obj.model] = X
            #startp_dict = model_obj.params2dict(model_obj.clipper(inits))

        print '\nDone fitting ' + model_obj.model + '.\n'
        # print 'Final results: '
        # X = model_obj.params2dict(model_obj.clipper(results_best[0:-2]))
        # for k, v in X.items():
        # print '\t' + k + ' = ' + str(v) + ','

        # print '\tLogLike = ' + str(results_best[-2])                        
        # print '\tAIC = ' + str(results_best[-1])
                

        

    # save final result in pickle
    with open(outputdir + 'chtc_ind_gs_'+dst,'wb') as f:
        pickle.dump(results, f)



