import pickle, sys, os
import pandas as pd
import numpy as np
import time
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweakRep
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
from Modules.Classes import PackerRep
from Modules.Classes import PackerEuc
import get_corr as gc
WT_THETA = 1.5
#Toggle 
pearson = True #fit correlations using pearson r. Uses spearman rho if false.
ll150 = 'hi' #Include only the participants with Packer negLL more than 150 when fit to full data (see slack conversation between Joe and Xian on 260219 for more context)


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
    runchunk = 93;
    
#Check that output directory exists, otherwise create it
pickledir = 'pickles/'
outputdir = pickledir + 'newpickles/'
if not os.path.isdir(outputdir):
    os.system('mkdir ' + outputdir)

#Get learning data
#data_assign_file = '../cat-assign/data/experiment.db'
data_assign_file = 'experiment-catassign.db'
con = sqlite3.connect(data_assign_file)
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * FROM assignment", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

#Get generation data
data_generate_file = 'experiment-midbot.db'
con = sqlite3.connect(data_generate_file)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()
    

if ll150 is 'hi':
    with open(pickledir+'ll150hi.p','rb') as f:
        includes = pickle.load(f)
    incCatAss = includes['includeCatAssign']
    incMidBot = includes['includeMidBot']
    info = info.loc[info.participant.isin(incCatAss)]
    assignment = assignment.loc[assignment.participant.isin(incCatAss)]
    stats = stats.loc[stats.participant.isin(incMidBot)]
    ll150str = 'll150hi'
elif ll150 is 'lo':
    with open(pickledir+'ll150lo.p','rb') as f:
        includes = pickle.load(f)
    incCatAss = includes['includeCatAssign']
    incMidBot = includes['includeMidBot']
    info = info.loc[info.participant.isin(incCatAss)]
    assignment = assignment.loc[assignment.participant.isin(incCatAss)]
    stats = stats.loc[stats.participant.isin(incMidBot)]
    ll150str = 'll150lo'
else:
    ll150str = ''
#execfile('validate_data.py')



# get data from pickle
# with open(pickledir+src, "rb" ) as f:
#     trials = pickle.load( f )

dataname = 'corr'+ll150str
filename = dataname
dst = 'best_params_{}.p'.format(filename)
print 'Grid Searching Correlation with Data: ' + dataname
#add chunk number to dst
dst = dst[0:-2] + '_chunk' + str(runchunk) + '.p'
dst_error = dst[0:-2] + '_error.p'


# options for the optimization routine
options = dict(
    method = 'Nelder-Mead',
    options = dict(maxiter = 500, disp = False),
    tol = 0.01,
) 



results = dict()
pptdata,tso = funcs.prep_corrvar(info,assignment,stimuli,stats,WT_THETA)
#Run grid search
for model_obj in [Packer,PackerEuc,RepresentJK13]:#[ConjugateJK13, RepresentJK13, CopyTweakRep, CopyTweak, Packer]:
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
        res = Simulation.hillclimber_corr(model_obj, pptdata, tso, options,
                                     inits=inits, results = False,
                                          callbackstyle='none',pearson=pearson)
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

