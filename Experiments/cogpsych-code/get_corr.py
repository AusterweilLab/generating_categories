#Spits out the correlation given some parameters fitted to individuals.
##NOTE: These functions have been moved to the Misc.py file. As it probably should be.

# def get_corr(start_params,pptdata,tso,model_obj,pearson=True,print_on = True):
#     execfile('Imports.py')
#     import Modules.Funcs as funcs
#     from Modules.Classes import Simulation
#     from Modules.Classes import CopyTweak
#     from Modules.Classes import Packer
#     from Modules.Classes import ConjugateJK13
#     from Modules.Classes import RepresentJK13
#     import pandas as pd
#     import math
#     import numpy as np
#     from scipy.stats import stats as ss

#     #Get log likelihoods
#     ll_list = []
#     print_ct = 0
#     for pi,pptdatarow in pptdata.iterrows():
#         params = start_params.copy()        
#         params['wts'] = pptdatarow['ppt_att']
#         if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
#             params['wts'] = 1.0 - params['wts']
#         #Initialise model (the value of the arguments here don't really matter)
#         model = model_obj(np.array([[0,0]]), params)
#         #pptdata = pd.DataFrame(columns = ['condition','betas'])
#         #transform parms
#         params = model.parmxform(params, direction = 1)
#         tso_ppt = tso[pi]
#         raw_array = []#np.zeros((1,nbetapermute))#np.zeros((nstim,nbetapermute))
#         for tso_ppti in tso_ppt:
#             #the neg loglikelihoods can get really large, which will tip it over to Inf when applying exp.
#             # To get around this, divide the nLL by some constant, exp it, add it to the prev prob, then log,
#             # and add it to the log of the same constant
#             raw_array_ps = tso_ppti.loglike(params,model_obj)
#             raw_array += [raw_array_ps]

#         raw_array_sum = np.array(raw_array) #raw_array.sum(0)    
#         raw_array_sum_max = raw_array_sum.max()
#         raw_array_t = np.exp(-(raw_array_sum - raw_array_sum_max)).sum()
#         raw_array_ll = -np.log(raw_array_t) + raw_array_sum_max

#         ll_list += [raw_array_ll]
#         if print_on:
#             #Print progress
#             print_ct = funcs.printProg(pi,print_ct,steps = 1, breakline = 20, breakby = 'char')            

#     #ll_list = np.atleast_2d(ll_list)
#     error_list = pptdata.ppterror.as_matrix()
#     if pearson:
#         corr = ss.pearsonr(ll_list,error_list)
#     else:
#         corr = ss.spearmanr(ll_list,error_list)
        
#     return corr




# def prep_corrvar(info,assignment,stimuli,stats,WT_THETA=1.5,print_on=True):
#     """
#     Prepares variables to be used in get_corr
#     """
#     execfile('Imports.py')
#     import Modules.Funcs as funcs
#     from Modules.Classes import Simulation
#     from Modules.Classes import CopyTweak
#     from Modules.Classes import Packer
#     from Modules.Classes import ConjugateJK13
#     from Modules.Classes import RepresentJK13
#     import pandas as pd
#     import math
#     import numpy as np
#     from scipy.stats import stats as ss

#     #Generate a list of all participant errors and their attention_weights
#     pptdata = pd.DataFrame(columns=['pptmatch','ppterror','ppt_att'])
#     #Prepare all trialset objects in the order of pptdata
#     tso = []
#     print_ct = 0
#     print 'Preparing trialset objects for each participant. This could take a couple of minutes.'
#     for i,row in info.iterrows():
#         ppt = row.participant
#         pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
#         nTrials = len(pptAssign)
#         accuracyEl = float(sum(pptAssign.correctcat == pptAssign.response))/nTrials
#         pptmatch = row.pptmatch
#         #Compute and add weights
#         pptOld = funcs.getCatassignID(pptmatch,source='match',fetch='old')
#         ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
#         #Find alphas and betas
#         pptloc = info['pptmatch']==pptmatch
#         #Get alphas with an ugly line of code
#         alphas  = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[0:4];
#         betas = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[4:8];        
#         pptdata = pptdata.append(
#             dict(pptmatch = pptmatch, ppterror = 1-accuracyEl,
#                  ppt_att = funcs.softmax(-ranges, theta = WT_THETA)[0]),            
#             ignore_index=True
#         )

#         #Add trialsetobj
#         alpha_vals = stimuli[alphas,:]
#         nstim = len(betas)
#         # Get all permutations of pptbeta and make a new trialObj for it
#         nbetapermute = math.factorial(nstim)
#         betapermute = [];
#         raw_array = np.zeros((1,nbetapermute))#np.zeros((nstim,nbetapermute))
#         tso_ppt = []
#         for beta in funcs.permute(betas):
#             categories = alphas
#             trials = range(nstim)
#             pptDF = pd.DataFrame(columns = ['participant','stimulus','trial','categories'])
#             pptDF.stimulus = pd.to_numeric(pptDF.stimulus)
#             #Initialise trialset object
#             pptTrialObj = Simulation.Trialset(stimuli)
#             pptTrialObj.task = 'generate'
#             for trial,beta_el in enumerate(beta):
#                     pptDF = pptDF.append(
#                             dict(participant=pptmatch, stimulus=beta_el, trial=trial, categories=[categories]),ignore_index = True
#                     )
#             pptTrialObj.add_frame(pptDF)
#             tso_ppt += [pptTrialObj]
#         tso += [tso_ppt]
#         if print_on:
#             print_ct = funcs.printProg(i,print_ct,steps = 1, breakline = 20, breakby = 'char')
            
#     return pptdata,tso
