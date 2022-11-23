#Gives a good idea of the distribution of generation probabilities at each step of exemplar generation
#given some parameter and alpha stimuli values
import pickle, math
import pandas as pd
import sys, os
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
from scipy.stats.stats import pearsonr
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
#Close figures
plt.close()

#load data
dataname_def = 'catassign'#'nosofsky1986'#'NGPMG1994'
participant_def = 'all' #cluster: 0,6,15; XOR: 10; row: 1,11; bottom: 208
unique_trials_def = 'all'
dataname = dataname_def
WT_THETA = 1.5 #for the attention weight fitting

narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    participant = int(sys.argv[1])
else:
    participant = participant_def

execfile('validate_data.py')

if dataname is 'catassign':
    ind = True #individual fits or not?    

# get data from pickle
with open(pickledir+src, "rb" ) as f:
    trials = pickle.load( f )
trials.task = task



if ind:
    parmspath = os.path.join(pickledir,'private','chtc_ind_gs_'+dst)
    #Get generation data for computation of individual weights,
    # if applicable
    if len(raw_db)>0:
        con = sqlite3.connect(raw_db)
        stats = pd.read_sql_query("SELECT * from betastats", con)
        con.close()

else:
    parmspath = os.path.join(pickledir,'chtc_gs_'+dst)

#Get best parms
with open(parmspath, "rb" ) as f:
    best_params_t = pickle.load( f )
best_params_tt = best_params_t.copy()
models = [Packer,CopyTweak,ConjugateJK13,RepresentJK13]
STAT_LIMS =  (-1.0, 1.0)

#populate participant list
if participant is 'all':
    pptlist = []
    for trial in trials.Set:
        for i in trial['participant']:
            pptlist = np.concatenate([pptlist,np.unique(i)])
    pptlist = np.unique(pptlist)
else:
    pptlist = [participant]
    
for ppt in pptlist: 
    #If it's individual fits, just take out the requested participant
    print 'Participant ' + str(ppt) + '... '
    if ind:
        best_params_t = dict()
        for modelname in best_params_tt.keys():
            best_params_t[modelname] = best_params_tt[modelname][ppt]
    #Rebuild it into a smaller dict
    best_params = dict()
    for modelname in best_params_t.keys():    
        best_params[modelname] = dict()
        for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
            parmval = best_params_t[modelname]['bestparmsll']
            best_params[modelname][parmname] = parmval[i]


    paramsP = best_params[Packer.model]
    paramsCT = best_params[CopyTweak.model]
    paramsJK = best_params[ConjugateJK13.model]
    paramsJKR = best_params[RepresentJK13.model]
    paramSet = [paramsP,paramsCT,paramsJK,paramsJKR]

    
    pptTrialObj = Simulation.extractPptData(trials,ppt,unique_trials_def)
    ntrials = len(pptTrialObj.Set)
    # plt.ioff()
    # plt.ion()
    f,ax = plt.subplots(ntrials,len(models),figsize = (8, 2*ntrials+2.5))
    ax.resize(ntrials,len(models))
    #Sort trial obj by trial number
    trialOrder = []
    for t,trialobj in enumerate(pptTrialObj.Set):
        nbeta = len(trialobj['categories'][1])
        pptTrialObj.Set[t]['trial'] = nbeta
        trialOrder += [nbeta]
    trialOrder = np.argsort(trialOrder)

    for trial in range(ntrials):
        # objIdx=0 #find the right trial in the trial obj
        # for obj in pptTrialObj.Set:
        #     if obj['trial']==trial:
        #         break
        #     objIdx += 1
        plotct = 0    
        categories = [pptTrialObj.stimuli[i,:] for i in pptTrialObj.Set[trialOrder[trial]]['categories'] if len(i)>0]

        A = categories[0]
        if trials.task is 'generate':
            resp = pptTrialObj.stimuli[pptTrialObj.Set[trialOrder[trial]]['response'],:]
            if len(categories)>1:
                #include the response
                B = np.append(categories[1],resp,axis=0)
            else:
                B = resp
        else:
            B = categories[1]
            #Calculate error rate
            error = 0
            numresp = 0
            for cat in range(len(pptTrialObj.Set[trialOrder[trial]]['categories'])):            
                catmembers = pptTrialObj.Set[trialOrder[trial]]['categories'][cat]
                response = pptTrialObj.Set[trialOrder[trial]]['response'][cat]
                numresp += len(response)
                checklist = np.zeros(len(response),dtype='bool')
                for checkmember in catmembers:
                    checklist += response == checkmember
                error += sum(1-checklist)
            error_rate = error/float(numresp)
            print 'Participant error: ' + str(round(error_rate,2))


        ps = []
        for i,model in enumerate(models):
            params = paramSet[i]
            if ind:
                #Apply weights
                pptOld = funcs.getCatassignID(int(ppt),source='analysis',fetch='old')
                ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
                params['wts'] = funcs.softmax(-ranges, theta = WT_THETA)[0]
                if model ==  ConjugateJK13 or model == RepresentJK13:
                    params['wts'] = 1.0 - params['wts']

            #reverse-transform
            #params = model.parmxform(params, direction = -1)
            ps += [model(categories,params,pptTrialObj.stimrange).get_generation_ps(pptTrialObj.stimuli,1,task)]

        plotVals = []
        psMax = 0
        psMin = 1
        #Get range
        for ps_el in ps:
            psMax = max(psMax,ps_el.max())
            psMin = min(psMin,ps_el.min())

        #Normalise all values
        psRange = psMax-psMin
        for i,ps_el in enumerate(ps):
            plotct += 1
            gps = funcs.gradientroll(ps_el,'roll')[:,:,0]
            #plotVals += [(gps-psMin)/psRange] #uncomment to implement normalisation
            ps_ElRange = gps.max()-gps.min();
            plotVals += [(gps-gps.min())/ps_ElRange]
            #ax = f.add_subplot(trials,2,plotct)
            #print B
            # beta colours - set last beta to some other colour
            betacol = ['green' for bi in range(len(B))]
            if task is 'generate':
                betacol[len(B)-1] = 'orange'

            im = funcs.plotgradient(ax[trial,i], plotVals[i], A, B, clim = STAT_LIMS, cmap = 'PuOr',beta_col=betacol)
            ax[trial,i].set_ylabel('Trial {}'.format(trial))
            # cbar = f.add_axes([0.21, .1, 0.55, 0.12])
            # f.colorbar(im, cax=cbar, ticks=[0, 1], orientation='horizontal')

        #Print probabilities up to trial num
        nll = np.zeros((ntrials,len(models)))
        for m,model in enumerate(models):
            params = paramSet[m]
            #params = model.parmxform(params, direction = -1)                        
            for t in range(trial+1):
                params = model.parmxform(params, direction = 1)
                nll[t,m] = pptTrialObj.loglike(params, model)
                # categoriesT = [pptTrialObj.stimuli[i,:] for i in pptTrialObj.Set[t]['categories'] if any(i)]
                # psT = model(categoriesT,params,pptTrialObj.stimrange).get_generation_ps(pptTrialObj.stimuli,1,task)
                # psT_raw = psT[pptTrialObj.Set[t]['response']]                
                # psT_raw[psT_raw<1e-308] = 1e-308
                # nll[t,m] = sum(-np.log(psT_raw))
                if t==0:
                    ax[t,m].set_title('{}'.format(models[m].modelshort))
                if t+1 == ntrials:
                    sum_nll = sum(nll[:,m])
                    parmstr = ''                
                    if ind and not 'wts' in models[m].parameter_names:
                        models[m].parameter_names += ['wts']
                    for parmname in models[m].parameter_names:
                        if parmname is 'wts':
                            parmvalnum1 = best_params[models[m].model][parmname][0]
                            parmvalnum2 = best_params[models[m].model][parmname][1]
                            parmval = '[{:.2},{:.2}]'.format(parmvalnum1,parmvalnum2)
                        else:
                            parmvalnum = best_params[models[m].model][parmname]
                            parmval = '{:.2E}'.format(parmvalnum)
                            if abs(float(parmval))<10000:
                                parmval = '{}'.format(round(best_params[models[m].model][parmname],2))
                        parmstr += '{} = {}\n'.format(funcs.get_initials(parmname,3),parmval)
                    if not task is 'generate':
                        error_str = 'Error = {}'.format(round(error_rate,2))
                    else:
                        error_str = ''
                    ax[t,m].set_xlabel('nLL = {}\n Total nLL = {}\n{}\n\n{}'.format(str(round(nll[t,m],2)),str(round(sum_nll,2)),error_str,parmstr))                    
                else:
                    ax[t,m].set_xlabel('nLL = {}'.format(str(round(nll[t,m],2))))

        #print nll

    #plt.tight_layout(w_pad=-4.0, h_pad= 0.5)
    plt.savefig('indfits/private/indheat{}.pdf'.format(int(ppt)))
    plt.cla()
    #plt.draw()
    #plt.ioff()
    #plt.show()

