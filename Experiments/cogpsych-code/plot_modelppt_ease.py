#Get the loglikelihoods of a given data set as a measure of how easy the model
#can generate that dataset
import pickle, math
import pandas as pd
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from scipy.stats.stats import pearsonr
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

#Specify simulation values
N_SAMPLES = 10000
WT_THETA = 1.5
MIN_LL = 1e-10

# Specify default dataname
dataname_def = 'midbot'#'nosofsky1986'#'NGPMG1994'
participant_def = 'all'
unique_trials_def = 'all'
dataname = dataname_def
execfile('validate_data.py')
# get data from pickle
with open(pickledir+src, "rb" ) as f:
	trials = pickle.load( f )

# get best params pickle
with open("pickles/chtc_gs_best_params_all_data_e1_e2.p", "rb" ) as f:
    best_params_t = pickle.load( f )
#Rebuild it into a smaller dict
best_params = dict()
for modelname in best_params_t.keys():    
    best_params[modelname] = dict()
    for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
        parmval = best_params_t[modelname]['bestparmsll']
        best_params[modelname][parmname] = parmval[i]
modelList = [ConjugateJK13,CopyTweak,Packer]                            

#Prepare matched database    
matchdb='../cat-assign/data_utilities/cmp_midbot.db'
        
unique_trials = 'all'
trials.task = task

#Get learning data
data_assign_file = '../cat-assign/data/experiment.db'
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

#Get unique ppts
pptlist = []#np.array([]);
for i,row in info.iterrows():
        pptlist += [row.pptmatch]
        #    pptlist = np.concatenate((pptlist,trial['participant']))


pptlist = np.unique(pptlist)

#see if ll_global exists as a pickle, otherwise construct new ll
modeleaseDB = "pickles/modelease_all_data_e1_e2.p"
try:
    with open(modeleaseDB, "rb" ) as f:
        ll_global = pickle.load( f )
        ll_loadSuccess = False
except:
    ll_global = dict()
    ll_loadSuccess = False
    
# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 


for model_obj in modelList:
    #model_obj = Packer
    model_name = model_obj.model

    if not ll_loadSuccess:
        #Get log likelihoods
        ll_list = []
        scale_constant = 1e308;
        print_ct = 0
        for ppt in pptlist:
            #since info contains the new mapping of ppts, and pptlist contains old,
            #convert ppt to new
            pptNew = ppt #
            pptOld = funcs.getMatch(pptNew,matchdb,fetch='Old')    
            pptloc = info['pptmatch']==pptNew
            #Get alphas with an ugly line of code
            As_num  = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[0:4];
            As = stimuli[As_num,:]
            params  = best_params[model_name]
            pptcondition = info['condition'].loc[pptloc].as_matrix()[0];
            pptbeta = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[4:8];
            nstim = len(pptbeta);    
            #Get weights
            ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
            params['wts'] = funcs.softmax(-ranges, theta = WT_THETA)[0]
            if model_obj ==  ConjugateJK13:
                params['wts'] = 1.0 - params['wts']

            #simulate
            model = model_obj([As], params)
            pptdata = pd.DataFrame(columns = ['condition','betas'])
            #transform parms
            params = model.parmxform(params, direction = 1)

            # Get all permutations of pptbeta and make a new trialObj for it
            nbetapermute = math.factorial(nstim)
            betapermute = [];
            likeli = 0 # np.zeros(len(pptbeta))#0
            likeli2 = 0 # np.zeros(len(pptbeta))#0
            raw_array = np.zeros((nstim,nbetapermute))

            for i,beta in enumerate(funcs.permute(pptbeta)):
                categories = As_num
                trials = range(nstim)
                pptDF = pd.DataFrame(columns = ['participant','stimulus','trial','condition','categories'])
                pptDF.stimulus = pd.to_numeric(pptDF.stimulus)
                pptTrialObj = Simulation.Trialset(stimuli)
                pptTrialObj.task = 'generate'
                for trial,beta_el in enumerate(beta):
                    pptDF = pptDF.append(
                        dict(participant=0, stimulus=beta_el, trial=trial, condition=pptcondition, categories=[categories]),ignore_index = True
                    )
                pptTrialObj.add_frame(pptDF)
                #the neg loglikelihoods can get really large, which will tip it over to Inf when applying exp.
                # To get around this, divide the nLL by some constant, exp it, add it to the prev prob, then log,
                # and add it to the log of the same constant
                raw_array_ps = pptTrialObj.loglike(params,model_obj,whole_array=True)
                raw_array[:,i] = -np.log(raw_array_ps)
                
                #likeli += np.exp(pptTrialObj.loglike(params,model_obj,whole_array=False) - np.log(scale_constant))
                #likeli2 += np.exp(pptTrialObj.loglike(params,model_obj,whole_array=False))
                #likeli += np.array(pptTrialObj.loglike(params,model_obj,whole_array=False)).flatten()
                
                #likeli = np.log(likeli) + np.log(scale_constant)
                raw_array_sum = raw_array.sum(0)    
                raw_array_sum_max = raw_array_sum.max()
                raw_array_t = sum(np.exp(raw_array_sum - raw_array_sum_max))
                raw_array_ll = np.log(raw_array_t) + raw_array_sum_max
                #execfile('plot_temp.py')
                #lll
            if likeli==np.inf:
                lll
                # print raw_array_t
                # print likeli
                # print np.log(likeli2)
            ll_list += [raw_array_ll]

            print_ct = funcs.printProg(ppt,print_ct,steps = 1, breakline = 20, breakby = 'char')
            #print ppt
    
            # retiring this bottom bit for now
            # for j in range(N_SAMPLES):
            #     gen = model.simulate_generation(stimuli,1,nexemplars = 4)
            #     model.forget_category(1)
            #     gen.sort()
            #     addrow = dict(condition = [pptcondition], betas = str(gen))        
            #     pptdata = pptdata.append(pd.DataFrame(addrow),ignore_index = True)
            
            # pptdata = pptdata.groupby(['condition','betas'])['betas']
            # pptdata = pptdata.agg(['size']);
            # pptdata = pptdata.reset_index();
            # betall = pptdata['size'].loc[pptdata['betas']==str(pptbeta)]        
            # if len(betall)<1:
            #     ll_one = MIN_LL
            # else:
            #     ll_one = betall
            # ll_list.append(ll_one)
            # print ll_one
            #This takes forever and never seems to captur pptbeta. Maybe calculate likelihoods analytically by adding the product of all possible combinations of pptbeta?
            
            #Old method, which is probably wrong anyway 200318
            # for ppt in pptlist:
            #     trialsPpt = Simulation.extractPptData(trials,int(ppt),unique_trials)
            #     #run fits
            #     res = Simulation.hillclimber(model_obj, trialsPpt, options,results=False,callbackstyle='none')
            #     #X = model_obj.params2dict(model_obj.clipper(res.x))
            #     ll_list.append(res['fun'])
            #     print '.'

        ll_list = np.atleast_2d(ll_list)
        pptlist2d = np.atleast_2d(pptlist)
        ll = np.concatenate((pptlist2d,ll_list),axis=0).T

        #sort
        ll = ll[ll[:,1].argsort()]
        #Add third col of zeros
        ll = np.concatenate((ll,np.atleast_2d(np.zeros(len(ll))).T),axis=1)    
    
        #attach ppt errors
        for i, row in info.iterrows():
            #fh, ax = plt.subplots(1,2,figsize = (12,6))
            ppt  = row.participant
            pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
            nTrials = len(pptAssign)
            accuracyEl = float(sum(pptAssign.correctcat == pptAssign.response))/nTrials


            pptNew = row.pptmatch
            #Prepare to plot configuration
            #get matched data
            #matched = funcs.getMatch(pptmatch,matchdb)
            #Add participant mean error to ll matrix
            ll[ll[:,0]==pptNew,2] = 1-accuracyEl

        ll_global[model_name] = ll
        
        #Save pickle for faster running next time
        with open(modeleaseDB, "wb" ) as f:
            pickle.dump(ll_global, f)

fh,axs = plt.subplots(1,len(modelList), figsize=(20,7))

for m,model_obj in enumerate(modelList):
    model_name = model_obj.model
    ll = ll_global[model_name]
    #Get correlations
    corr = pearsonr(ll[:,1],ll[:,2])
    cov = np.cov(ll[:,1],ll[:,2])
    print model_name
    print '\tr = ' + str(corr[0])
    print '\tp = ' + str(corr[1])
    ax = axs[m]
    #Plot figure
    ax.scatter(ll[:,1],ll[:,2])

    #Add best fit line
    coeff = np.polyfit(ll[:,1],ll[:,2],1)
    x = np.array([min(ll[:,1]),max(ll[:,1])])
    y = x*coeff[0] + coeff[1]
    ax.plot(x,y,'--')
    ax.set_title('r = {:.3}, p = {:.2e}'.format(corr[0],corr[1]))
    ax.set_xlabel('{} negLL'.format(model_name))
    ax.set_ylabel('Participant p(error)')
    
plt.savefig('modelvsppt.png')
    #plt.cla()
