#Spits out the correlation given some parameters fitted to individuals.



def get_corr(start_params,pptdata,model_obj,stimuli,pearson=True,print_on = True):
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

    #Get log likelihoods
    ll_list = []
    print_ct = 0
    for i,pptdatarow in pptdata.iterrows():
        params = start_params.copy()        
        params['wts'] = pptdatarow['ppt_att']
        pptmatch = pptdatarow['pptmatch']
        alphas = pptdatarow['alphas']
        betas = pptdatarow['betas']
        alpha_val = stimuli[alphas,:]
        nstim = len(betas) 
        if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
            params['wts'] = 1.0 - params['wts']
        #Initialise model (the value of the arguments here don't really matter)
        model = model_obj([alpha_val], params)
        #pptdata = pd.DataFrame(columns = ['condition','betas'])
        #transform parms
        params = model.parmxform(params, direction = 1)

        # Get all permutations of pptbeta and make a new trialObj for it
        nbetapermute = math.factorial(nstim)
        betapermute = [];
        raw_array = np.zeros((1,nbetapermute))#np.zeros((nstim,nbetapermute))
        for i,beta in enumerate(funcs.permute(betas)):
            categories = alphas
            trials = range(nstim)
            pptDF = pd.DataFrame(columns = ['participant','stimulus','trial','categories'])
            pptDF.stimulus = pd.to_numeric(pptDF.stimulus)
            #Initialise trialset object
            pptTrialObj = Simulation.Trialset(stimuli)
            pptTrialObj.task = 'generate'
            for trial,beta_el in enumerate(beta):
                    pptDF = pptDF.append(
                            dict(participant=pptmatch, stimulus=beta_el, trial=trial, categories=[categories]),ignore_index = True
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
            #Print progress
            print_ct = funcs.printProg(pptmatch,print_ct,steps = 1, breakline = 20, breakby = 'char')            

    #ll_list = np.atleast_2d(ll_list)
    error_list = pptdata.ppterror.as_matrix()
    if pearson:
        corr = ss.pearsonr(ll_list,error_list)
    else:
        corr = ss.spearmanr(ll_list,error_list)
        
    return corr

    
    #pptlist2d = np.atleast_2d(pptlist)
    #    ll = np.concatenate((pptlist2d,ll_list),axis=0).T

    # #sort
    # ll = ll[ll[:,1].argsort()]
    # #Add third col of zeros
    # ll = np.concatenate((ll,np.atleast_2d(np.zeros(len(ll))).T),axis=1)    

    # #attach ppt errors
    # for i, row in info.iterrows():
    #     #fh, ax = plt.subplots(1,2,figsize = (12,6))
    #     ppt  = row.participant
    #     pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
    #     nTrials = len(pptAssign)
    #     accuracyEl = float(sum(pptAssign.correctcat == pptAssign.response))/nTrials


    #     pptNew = row.pptmatch
    #     #Prepare to plot configuration
    #     #get matched data
    #     #matched = funcs.getMatch(pptmatch,matchdb)
    #     #Add participant mean error to ll matrix
    #     ll[ll[:,0]==pptNew,2] = 1-accuracyEl



