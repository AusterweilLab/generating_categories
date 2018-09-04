#Get the loglikelihoods of a given data set as a measure of how easy the model
#can generate that dataset
import pickle, math
import pandas as pd
import sqlite3
import random
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import CopyTweakRep
from Modules.Classes import Packer
from Modules.Classes import PackerRep
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
from scipy.stats import stats as ss
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

pearson = True
if pearson:
    corrtype = 'p'
else:
    corrtype = 's'
#Bootstrap parameters
nbootstraps = 1000

savefilename='modelvsppt{}_t.pdf'.format(corrtype)
bestparmdb = "pickles/chtc_gs_best_params_corr{}.p".format(corrtype)
modeleaseDB = "pickles/modelease_corr{}.p".format(corrtype)
#Some plotting options
font = {'family' : 'DejaVu Sans',
        'weight' : 'regular',
        'size'   : 20}
show_p = False #show pearson r in plots
show_s = False #show spearman tho in plots

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


plt.rc('font', **font)

# get data from pickle
with open(pickledir+src, "rb" ) as f:
    trials = pickle.load( f )

# get best params pickle
#bestparmdb = "pickles/chtc_gs_best_params_all_data_e1_e2.p"
#bestparmdb = "pickles/chtc_gs_best_params_corrs.p"
with open(bestparmdb, "rb" ) as f:
    best_params_t = pickle.load( f )

#Rebuild it into a smaller dict
best_params = dict()
for modelname in best_params_t.keys():    
    best_params[modelname] = dict()
    for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
        parmval = best_params_t[modelname]['bestparmsll']
        best_params[modelname][parmname] = parmval[i]
modelList = [Packer,CopyTweak,ConjugateJK13,RepresentJK13]
#modelList = [CopyTweak,CopyTweakRep,Packer, RepresentJK13,]                            

#Specify plot order
modelPlotOrder = np.array([[Packer,RepresentJK13],[CopyTweak,ConjugateJK13]])
#modelPlotOrder = np.array([[CopyTweak,CopyTweakRep],[Packer,RepresentJK13]])

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

#Specify a few more bootstrap parameters
nsamples = len(pptlist)
nsamprange = range(nsamples)


pptlist = np.unique(pptlist)
#see if ll_global exists as a pickle, otherwise construct new ll
ll_loadSuccess = {}
for model in modelList:
    ll_loadSuccess[model.model] = False
    
try:
    with open(modeleaseDB, "rb" ) as f:
        ll_global = pickle.load( f )
        #Check that model name exists in global, otherwise run it again
        for model in modelList:
            if model.model in ll_global.keys():
                ll_loadSuccess[model.model] = True
except:
    ll_global = dict()
    #ll_loadSuccess = False
    
# options for the optimization routine
options = dict(
    method = 'Nelder-Mead',
    options = dict(maxiter = 500, disp = False),
    tol = 0.01,
) 


#Prepare corr var
if 'tso' not in ll_global.keys():
    pptdata,tso = funcs.prep_corrvar(info,assignment,stimuli,stats,WT_THETA)
    ll_global['tso'] = tso
    ll_global['pptdata'] = pptdata
else:
    tso = ll_global['tso']

for model_obj in modelList:
    #model_obj = Packer
    model_name = model_obj.model
    if not ll_loadSuccess[model_name]:
        #Get log likelihoods
        ll_list = []
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
            if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
                params['wts'] = 1.0 - params['wts']
            #transform parms
            model = model_obj([As], params)
            params = model.parmxform(params, direction = 1)
            
            # Get all permutations of pptbeta and make a new trialObj for it
            nbetapermute = math.factorial(nstim)
            betapermute = [];
            raw_array = np.zeros((1,nbetapermute))
            categories = [As_num,pptbeta]
            #Get loglikelihoods
            raw_array_ll = Simulation.loglike_allperm(params, model_obj, categories, stimuli, permute_category = 1)
            ll_list += [raw_array_ll]
            #print categories,raw_array_ll
            print_ct = funcs.printProg(ppt,print_ct,steps = 1, breakline = 20, breakby = 'char')

        #Re-organise the lists
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
#fh,axs = plt.subplots(2,int(np.ceil(len(modelList)/2)), figsize=(20,8))
fh,axs = plt.subplots(2,int(np.ceil(len(modelList)/2)), figsize=(15,15))
plt.tight_layout(w_pad=1,h_pad=5.0,rect=(.05,.05,.95,.95))
for m,model_obj in enumerate(modelList):
    model_loc = modelPlotOrder==model_obj
    ax = axs[model_loc][0]
    model_name = model_obj.model
    model_print = model_obj.modelprint
    ll = ll_global[model_name]
    #Get correlations
    corr_p = ss.pearsonr(ll[:,1],ll[:,2])
    corr_s = ss.spearmanr(ll[:,1],ll[:,2])
    cov = np.cov(ll[:,1],ll[:,2])
    #Run bootstrap
    corr_bs_p = []
    corr_bs_s = []
    bestfitlines = []
    if not pearson:
        rankorderx_base = np.array(range(len(ll[:,1])))
        rankordery_base = ll[:,2].argsort()
    for bsi in range(nbootstraps):
        bs_samples = [random.choice(nsamprange) for ct in nsamprange]
        ll_bs = ll[bs_samples,:]
        corr_bs_p += [ss.pearsonr(ll_bs[:,1],ll_bs[:,2])[0]]            
        corr_bs_s += [ss.spearmanr(ll_bs[:,1],ll_bs[:,2])[0]]
        if pearson:
            #Find best fit line        
            bscoeff = np.polyfit(ll_bs[:,1],ll_bs[:,2],1)
            xrange_bs = np.linspace(min(ll[:,1]),max(ll[:,1]),100)
        else:
            rankorderx = rankorderx_base[bs_samples]            
            rankordery = rankordery_base[bs_samples]
            #Add best fit line
            bscoeff = np.polyfit(rankorderx,rankordery,1)
            xrange_bs = np.linspace(min(rankorderx),max(rankorderx),100)            
        bestfitlines += [bscoeff]
    #Get upper and lower 95% percentile of y at each x
    yrangeLL = []
    yrangeUL = []
    for xi in xrange_bs:
        yrangeAll = [xi*bfl[0] + bfl[1] for bfl in bestfitlines]
        yrangePct = np.percentile(yrangeAll,(2.5, 97.5))
        yrangeLL += [yrangePct[0]]
        yrangeUL += [yrangePct[1]]
    ax.plot(xrange_bs,yrangeUL,'g:')
    ax.plot(xrange_bs,yrangeLL,'g:')
    
    #Get 95% CI
    ci_95_p = np.percentile(corr_bs_p,(2.5, 97.5))
    ci_95_s = np.percentile(corr_bs_s,(2.5, 97.5))
        
    print model_name
    print '\tPearson  r   = {:.3f} 95%CI[{:.3f},{:.3f}], p = {:.2e}'.format(
        corr_p[0],ci_95_p[0],ci_95_p[1],corr_p[1])
    #print '\tp = ' + str(corr[1])
    print '\tSpearman rho = {:.3f} 95%CI[{:.3f},{:.3f}], p = {:.2e}'.format(
        corr_s[0],ci_95_s[0],ci_95_s[1],corr_s[1])
    #Plot figure
    if pearson:
        ax.scatter(ll[:,1],ll[:,2])
        #Add best fit line
        coeff = np.polyfit(ll[:,1],ll[:,2],1)
        x = np.array([min(ll[:,1]),max(ll[:,1])])
        y = x*coeff[0] + coeff[1]
        #Find ideal position for text
        xrange = ax.get_xlim()
        textx = (xrange[1]-xrange[0])*.1+xrange[0]
        texty = .62
        #Specify axis label strings
        xlabel = 'negLL'
        ylabel = 'Participant p(error)'
    else:
        rankorderx = range(len(ll[:,1]))
        rankordery = ll[:,2].argsort()
        ax.scatter(rankorderx,rankordery)
        #Add best fit line
        coeff = np.polyfit(rankorderx,rankordery,1)
        x = np.array([min(rankorderx),max(rankorderx)])
        y = x*coeff[0] + coeff[1]
        #Find ideal position for text
        xrange = ax.get_xlim()
        yrange = ax.get_ylim()
        textx = (xrange[1]-xrange[0])*.1+xrange[0]
        texty = (yrange[1]-yrange[0])*.85+yrange[0]
        xlabel = 'negLL rank order'
        ylabel = 'Participant p(error) rank order '
        
    #Format presentation of correlation values
    if show_p:
        titlestr_p = 'r = {:.3}, p = {:.2e}'.format(corr_p[0],corr_p[1])
    else:
        titlestr_p = ''
    if show_s:        
        rho = r'$\rho$'
        titlestr_s = '{} = {:.3}, p = {:.2e}'.format(rho,corr_s[0],corr_s[1])
    else:
        titlestr_s = ''
    if show_p and show_s:
        titlestr_all = '{}\n{}'.format(titlestr_p,titlestr_s)
    else:
        if show_p:
            titlestr_all = '{}'.format(titlestr_p)
        elif show_s:
            titlestr_all = '{}'.format(titlestr_s)
        else:
            titlestr_all = ''
    ax.text(textx,texty,titlestr_all,fontsize=12)
    ax.plot(x,y,'--')
    ax.set_title(model_print)
    ax.set_xlabel(xlabel)
    #ax.set_title('{}\n{}'.format(titlestr_p, titlestr_s),fontsize=12)
    #ax.set_xlabel('negLL\n{}'.format(model_print))
    first_col = np.where(model_loc)    
    if first_col[1][0]==0:
        ax.set_ylabel(ylabel)
    else:
        ax.set_ylabel('')
        ax.set_yticklabels([])
    
plt.savefig(savefilename)
plt.cla()

#Also print the likelihood ratio test results for PACKER vs CopyTweak
# This is simply -2(LL_Packer - LL_CopyTweak)
#280618  - ok likelihood ratio test doesn't seem to make sense. Run bootstrap instead.
#Get global generation LL using these parameters
# global_ll_packer = trials.loglike(best_params['PACKER'],Packer,parmxform=False)
# global_ll_copytweak = trials.loglike(best_params['Copy and Tweak'],CopyTweak,parmxform=False)

# from scipy import stats as s2
# ll_ratio = -2.0 * (global_ll_packer - global_ll_copytweak)
# pval = s2.chi2.sf(ll_ratio,1);

# print "Likelihood ratio test:"
# print "\t chi_sq (1) = {}, p = {:.3}".format(ll_ratio,pval)

