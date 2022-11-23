#Plot a scatterplot of error likelihoods vs category assignment likelihoods
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
from Modules.Classes import RepresentJK13
from scipy.stats import stats as ss
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

#Specify simulation values
N_SAMPLES = 10000
WT_THETA = 1.5
MIN_LL = 1e-10

#Toggle
fit_weights = True #add calculation of weights to the generation of LL
fit_ind = True
# Specify default dataname
dataname_def = 'catassign'#'nosofsky1986'#'NGPMG1994'
participant_def = 'all'
unique_trials_def = 'all'
dataname = dataname_def
execfile('validate_data.py')

#Some plotting options
font = {'family' : 'DejaVu Sans',
        'weight' : 'regular',
        'size'   : 18}

plt.rc('font', **font)

# get data from pickle
with open(pickledir+src, "rb" ) as f:
    trials = pickle.load( f )

    
# get best params pickle
#bestparamdb = "pickles/chtc_gs_best_params_all_data_e1_e2.p"
if fit_ind:
    bestparamdb = "pickles/private/chtc_ind_gs_best_params_catassign.p"
else:
    bestparamdb = "pickles/chtc_gs_best_params_catassign.p"
bestparamerrdb = "pickles/chtc_gs_best_params_catassign.p"
#bestparamerrdb = "pickles/chtc_gs_best_params_catassign_fit2err.p"
with open(bestparamdb, "rb" ) as f:
    best_params_t = pickle.load( f )

with open(bestparamerrdb, "rb" ) as f:
    best_params_err_t = pickle.load( f )

#Rebuild it into a smaller dict
best_params = dict()

if fit_ind:
    models = best_params_t.keys()
    if 'fit_weights' in models:
        models.remove('fit_weights')
    for modelname in models:
        best_params[modelname] = dict()
        for ppt in best_params_t[modelname].keys():    
            best_params[modelname][ppt] = dict()
            for i,parmname in enumerate(best_params_t[modelname][ppt]['parmnames']):
                parmval = best_params_t[modelname][ppt]['bestparmsll']
                best_params[modelname][ppt][parmname] = parmval[i]
    #Rebuild it into a smaller dict
else:
    for modelname in best_params_t.keys():    
        best_params[modelname] = dict()
        for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
            parmval = best_params_t[modelname]['bestparmsll']
            best_params[modelname][parmname] = parmval[i]
#Rebuild it into a smaller dict
best_params_err = dict()
for modelname in best_params_err_t.keys():    
    best_params_err[modelname] = dict()
    for i,parmname in enumerate(best_params_err_t[modelname]['parmnames']):
        parmval = best_params_err_t[modelname]['bestparmsll']
        best_params_err[modelname][parmname] = parmval[i]


modelList = [Packer,CopyTweak,ConjugateJK13,RepresentJK13]                            

#Prepare matched database    
matchdb='../cat-assign/data_utilities/cmp_midbot.db'
        
#unique_trials = 'all'
trials.task = task

#Get learning data
data_assign_file = '../cat-assign/data/experiment.db'
con = sqlite3.connect(data_assign_file)
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * FROM assignment", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()
#and learning trialobj

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

#see if llg exists as a pickle, otherwise construct new ll
if fit_ind:
    errcatDB = "pickles/errcatind.p"
else:
    errcatDB = "pickles/errcat.p"

try:
    with open(errcatDB, "rb" ) as f:
        llg = pickle.load( f ) #llglobal
        ll_loadSuccess = False
except:
    llg = dict()
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
        ll_list_err = []
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
            pptcondition = info['condition'].loc[pptloc].as_matrix()[0];
            pptbeta = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[4:8];
            nstim = len(pptbeta);    
            #transform parms            
            if fit_ind:
                pptAnalysis = funcs.getCatassignID(pptNew,source='match',fetch='analysis')
                params = best_params[model_name][pptAnalysis]
            else:
                params = best_params[model_name]
                
            model = model_obj([As], params)
            params = model.parmxform(params, direction = 1)

            params_err  = best_params_err[model_name]
            model = model_obj([As], params_err)
            params_err = model.parmxform(params_err, direction = 1)
            #Get weights
            if fit_weights:
                ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
                params['wts'] = funcs.softmax(-ranges, theta = WT_THETA)[0]
                if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
                    params['wts'] = 1.0 - params['wts']                    
                params_err['wts'] = params['wts']
            #Extract ppt-unique trialobj
            # Note that ppt numbers in the trialset
            # object are of the 'analysis' type, while the ppt numbers in this
            # loop are of the 'match' type
            pptAnalysis = funcs.getCatassignID(ppt,fetch='analysis',source='match')
            pptTrialObj = Simulation.extractPptData(trials,pptAnalysis)
            pptTrialObj.task = 'assign'
            catassign_ll = pptTrialObj.loglike(params,model_obj)
            pptTrialObj.task = 'error'
            error_ll = pptTrialObj.loglike(params_err,model_obj)
            ll_list += [catassign_ll]
            ll_list_err += [error_ll]
            print_ct = funcs.printProg(ppt,print_ct,steps = 1, breakline = 20, breakby = 'char')
            #print ppt

        ll_list = np.atleast_2d(ll_list)
        ll_list_err = np.atleast_2d(ll_list_err)
        pptlist2d = np.atleast_2d(pptlist)
        ll = np.concatenate((pptlist2d,ll_list,ll_list_err),axis=0).T
        
        #sort
        ll = ll[ll[:,1].argsort()]
        #Add third col of zeros
        #ll = np.concatenate((ll,np.atleast_2d(np.zeros(len(ll))).T),axis=1)    

        
        llg[model_name] = ll
        
        #Save pickle for faster running next time
        with open(errcatDB, "wb" ) as f:
            pickle.dump(llg, f)

fh,axs = plt.subplots(1,len(modelList), figsize=(20,8))

for m,model_obj in enumerate(modelList):
    model_name = model_obj.model
    model_short = model_obj.modelshort
    ll = llg[model_name]
    #Get correlations
    corr_p = ss.pearsonr(ll[:,1],ll[:,2])
    corr_s = ss.spearmanr(ll[:,1],ll[:,2])
    cov = np.cov(ll[:,1],ll[:,2])
    print model_name
    print '\tPearson  r   = {:.3}, p = {:.2e}'.format(corr_p[0],corr_p[1])
    #print '\tp = ' + str(corr[1])
    print '\tSpearman rho = {:.3}, p = {:.2e}'.format(corr_s[0],corr_s[1])
    ax = axs[m]
    #Plot figure
    ax.scatter(ll[:,1],ll[:,2])

    #Add best fit line
    coeff = np.polyfit(ll[:,1],ll[:,2],1)
    x = np.array([min(ll[:,1]),max(ll[:,1])])
    y = x*coeff[0] + coeff[1]
    titlestr_p = 'r = {:.3}, p = {:.2e}'.format(corr_p[0],corr_p[1])
    rho = r'$\rho$'
    titlestr_s = '{} = {:.3}, p = {:.2e}'.format(rho,corr_s[0],corr_s[1])
    ax.plot(x,y,'--')
    ax.set_title('{}\n{}'.format(titlestr_p, titlestr_s),fontsize=16)
    if fit_ind:
        ax.set_xlabel('categorization (ind) negLL\n{}'.format(model_short))
    else:        
        ax.set_xlabel('categorization negLL\n{}'.format(model_short))
    if m==0:
        ax.set_ylabel('error negLL')
    else:
        ax.set_ylabel('')
        ax.set_yticklabels([])

if fit_ind:        
    plt.savefig('errvscatind.pdf')
else:
    plt.savefig('errvscat.pdf')
    
plt.cla()
