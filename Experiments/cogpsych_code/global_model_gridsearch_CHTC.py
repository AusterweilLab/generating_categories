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
from Modules.Classes import CopyTweakRep
from Modules.Classes import PackerRep
from Modules.Classes import PackerEuc
from Modules.Classes import NegatedSpace
from Modules.Classes import NConjugateJK13
from Modules.Classes import NRepresentJK13
from Modules.Classes import NPacker
from Modules.Classes import NCopyTweak
#Toggle 
fit_weights = False #This is a little difficult to do at this stage. I'll keep the application of weights to after the global fits have been done.010618
fiterror = False #Toggle if fitting error
ll150 = '' #either 'hi' or 'lo'. Include only the participants with Packer negLL more than 150 when fit to full data (see slack conversation between Joe and Xian on 260219 for more context)

# Specify default dataname
datasets  = ['corner','xcrA','xcrB','xcrC']#['5con','5con_s','corner','corner_s','corner_c','pooled','pooled-no1st']#['corner','corner_s','corner_c','5con','5con_s']#['pooled','pooled-no1st']#xcrABC
modelList = [NegatedSpace,NConjugateJK13, NRepresentJK13, NPacker, NCopyTweak,ConjugateJK13,RepresentJK13,Packer,CopyTweak,CopyTweakRep]#[ConjugateJK13, RepresentJK13, CopyTweakRep, CopyTweak, Packer]
 #dataname_def = 'nosofsky1986'
participant_def = 'all'
unique_trials_def = 'all'
nchunks = 1000 #number of CHTC instances to run
#Allow for input arguments at the shell
narg = len(sys.argv)

if __name__ == "__main__" and narg>1:
    participant = participant_def
    unique_trials = unique_trials_def
    runchunk = int(sys.argv[1]) #first arg from terminal is chunk idx
else:
    #dataname = dataname_def
    participant = participant_def
    unique_trials = unique_trials_def
    runchunk = 11;
    
#datasets = ['pooled','pooled-no1st','xcr','midbot','catassign','nosofsky1986','nosofsky1989','NGPMG1994']        

#Check that output directory exists, otherwise create it
pickledir = 'pickles/'
outputdir = pickledir + 'newpickles/'
if not os.path.isdir(outputdir):
    os.system('mkdir ' + outputdir)


if ll150 is 'hi':
    with open(pickledir+'ll150hi.p','rb') as f:
        includes = pickle.load(f)
    include = includes['includeMidBot']
    participant = include
    ll150str = 'll150hi'
elif ll150 is 'lo':
    with open(pickledir+'ll150lo.p','rb') as f:
        includes = pickle.load(f)
    include = includes['includeMidBot']
    participant = include
    ll150str = 'll150lo'
else:
    ll150str = ''

for dataname in datasets:
    execfile('validate_data.py')
    dst = dst[0:-2] + ll150str + dst[-2:]
    
    print 'Grid Searching Data: ' + dataname
    
    # get data from pickle
    with open(pickledir+src, "rb" ) as f:
        trials = pickle.load( f )

    if fiterror:
        #Force task to fit error, and append err to dst filename
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

    for model_obj in modelList:
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
        results_array = np.array(np.zeros([nfits,nparms+2])) #nparms+1 cols, where +2 is the LL and AIC
        results_model = dict()

        print 'Fitting: ' + model_obj.model
        print 'Total possible starting points: {}'.format(nfitsTotal)
        print 'Running chunk {}, extracting starting points: [{}:{}]'.format(runchunk, chunkIdxStart, chunkIdxEnd)
        print 'Total starting points extracted: ' + str(nfits)
        printcol = 20
        if nfits==0:
            print 'No starting points extracted, moving on.\n'
            continue
        for i in range(nfits):
            if np.mod(i+1,printcol) != 0:
                print str(i),
                sys.stdout.flush()
            else:
                print str(i)
            
            inits = startp[i,:]
            res = Simulation.hillclimber(model_obj, trials, options,
                                         inits=inits, results = False,
                                         callbackstyle='none') #can use 'iter','none','.'
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
        results[model_obj.model] = results_model
        #X = model_obj.params2dict(model_obj.clipper(res.x))
        #results[model_obj.model] = X
        #startp_dict = model_obj.params2dict(model_obj.clipper(inits))
        print '\nDone fitting ' + model_obj.model + '.\n'
        print 'Final results: '
        X = model_obj.params2dict(model_obj.clipper(results_best[0:-2]))
        for k, v in X.items():
            print '\t' + k + ' = ' + str(v) + ','

        print '\tLogLike = ' + str(results_best[-2])                        
        print '\tAIC = ' + str(results_best[-1])
                
        #for k,v in results.items():
        #    print k, v

        

    # save final result in pickle
    with open(outputdir + 'chtc_gs_'+dst,'wb') as f:
        #pass 
        pickle.dump(results, f)

#Simulation.print_gs_nicenice()

