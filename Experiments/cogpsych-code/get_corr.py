#Spits out the correlation given some parameters fitted to individuals.
#This script is meant to be run in some other external script using execfile. Really bad way to do things but until I can be motivated to write this a little better, this is going to be the way things are for now, sorry!



def get_corr(start_params,pptlist,model_obj,info,assignment,stimuli,stats,WT_THETA = 1.5,print_on = True):
    execfile('Imports.py')
    import Modules.Funcs as funcs
    from Modules.Classes import Simulation
    from Modules.Classes import CopyTweak
    from Modules.Classes import Packer
    from Modules.Classes import ConjugateJK13
    from Modules.Classes import RepresentJK13
    import pandas as pd
    import math
    import numpy as np
    from scipy.stats import stats as ss

    #Prepare matched database    
    matchdb='../cat-assign/data_utilities/cmp_midbot.db'
    #Get log likelihoods
    ll_list = []
    scale_constant = 1e308;
    print_ct = 0
    for ppt in pptlist:
        params = start_params.copy()
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
        #Get weights
        ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
        params['wts'] = funcs.softmax(-ranges, theta = WT_THETA)[0]
        if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
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
        raw_array = np.zeros((1,nbetapermute))#np.zeros((nstim,nbetapermute))
        a = 2

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
            raw_array_ps = pptTrialObj.loglike(params,model_obj)
            raw_array[:,i] = raw_array_ps

            #end of loop

        raw_array_sum = raw_array #raw_array.sum(0)    
        raw_array_sum_max = raw_array_sum.max()
        raw_array_t = np.exp(-(raw_array_sum - raw_array_sum_max)).sum()
        raw_array_ll = -np.log(raw_array_t) + raw_array_sum_max

        ll_list += [raw_array_ll]
        if print_on:
            print_ct = funcs.printProg(ppt,print_ct,steps = 1, breakline = 20, breakby = 'char')            

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

    corr = ss.pearsonr(ll[:,1],ll[:,2])
    return corr


