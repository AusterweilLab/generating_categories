import scipy.optimize as op
import scipy.stats as ss
import numpy as np
import sys

import Modules.Funcs as funcs

currmodel='' #temp
currtrials=''
callback = ''
itcount = 0

class Trialset(object):

    """
    A class representing a collection of trials
        Data (i.e., responses) is saved in a list Set
    """
        
    def __init__(self, stimuli):
        
        # figure out what the stimulus domain is        
        self.stimuli = stimuli
        self.stimrange,self.stimstep = funcs.getrange(stimuli)
                
        # initialize trials list
        self.Set = [] # compact set
        self.nunique = 0
        self.nresponses = 0
        self.task = ''
        self.nparticipants = 0
        self.participants = []
                
    def __str__(self):
        S  = 'Trialset containing: ' 
        S += '\n\t ' + str(self.nunique) + ' unique trials '
        S += '\n\t ' + str(self.nresponses) + ' total responses'
                # S += '\nTask: ' + self.task
        return S

    def _update(self):
        self.nunique = len(self.Set)
        self.nresponses = sum([len(i['response']) for i in self.Set])
 
    def add(self, response, categories = [], participant = [], wrap_ax = None):
        """Add a single trial to the trial lists
                
        If response variable is a scalar (responseType=1), then add response to only one
        category. If response variable is a 2-element list (responseType=2), then add the
        value of the first element to the category specified by the
        second element.
        
        Also add participant information and if axis needs to be wrapped(if available)
        
        030819 Gonna phase out type 1 responseTypes, since type 2 is more general.
        """
        
        if type(response) is not list:
            add2cat = None
            responseType = 1
            response = response
        elif type(response) is list:
            if len(response) == 2:
                add2cat = response[1]
                responseType = 2
                response = response[0]                                
            else:
                raise ValueError('The "response" variable needs',\
                                 'to be either a single number,',\
                                 'or a a list containing',\
                                 'only 2 elements.')

            
        #Force wrap_ax to be int or None
        if hasattr(wrap_ax,'__len__'):
            if len(wrap_ax)==0:
                wrap_ax = None
        if not wrap_ax is None:
            if np.isnan(wrap_ax):
                wrap_ax = None
            else:
                wrap_ax = int(wrap_ax)
        # sort category lists, do a lookup
        categories = [np.sort(i) for i in categories]
        idx = self._lookup(categories)
        # if there is no existing configuration, add a new one
        if idx is None:
            self.nunique += 1            
            if responseType == 1:
                self.Set.append(dict(
                    response = np.array([response]), 
                    categories = categories,
                    participant = np.array([participant]),
                    wrap_ax = np.array([wrap_ax])
                )
                )
            elif responseType == 2:
                ncat = len(categories)
                if add2cat==ncat:
                    ncat +=1
                    categories += [np.array([])]
                respList =  [np.array([],dtype=int) for _ in xrange(ncat)]
                pList = [np.array([],dtype=int) for _ in xrange(ncat)]
                wrapList = [np.array([],dtype=int) for _ in xrange(ncat)]
                respList[add2cat] = np.append(respList[add2cat],response)
                pList[add2cat] = np.append(pList,participant)
                wrapList[add2cat] = np.append(wrapList,wrap_ax)
                
                self.Set.append(dict(
                    response = respList,
                    categories = categories,
                    participant = pList,
                    wrap_ax = wrapList)
                )

        # if there is an index, just add the response
        else:
            if responseType == 1:
                self.Set[idx]['response'] = np.append(
                    self.Set[idx]['response'], response)
                self.Set[idx]['participant'] = np.append(
                    self.Set[idx]['participant'], participant)
                self.Set[idx]['wrap_ax'] = np.append(
                    self.Set[idx]['wrap_ax'], wrap_ax)
            elif responseType == 2:
                #ncat = len(categories)
                #if add2cat==ncat:                
                if add2cat==len(self.Set[idx]['response']):
                    categories += [np.array([])]
                    self.Set[idx]['response'] += [np.array([])]
                    self.Set[idx]['participant'] += [np.array([])]
                    self.Set[idx]['wrap_ax'] += [np.array([])]

                self.Set[idx]['response'][add2cat] = np.append(
                    self.Set[idx]['response'][add2cat],response)
                self.Set[idx]['participant'][add2cat] = np.append(
                    self.Set[idx]['participant'][add2cat],participant)
                self.Set[idx]['wrap_ax'][add2cat] = np.append(
                    self.Set[idx]['wrap_ax'][add2cat],wrap_ax)

                #self.Set[idx]['response'][add2cat] = np.append(
                #        self.Set[idx]['response'][add2cat],response)
                #Hmm, why can't I just use self.Set[idx]['response']...
                #...[add2cat].append(response)?

        #Add participant to list of unique participants
        if isinstance(participant,int):
            if not participant in self.participants:
                self.participants = np.append(self.participants,participant)
                self.nparticipants += 1
        else: #if list or array
            for pel in participant:
                if not pel in self.participants:
                    self.participants = np.append(self.participants,pel)
                    self.nparticipants += 1

        # increment response counter
        self.nresponses += 1
                
    def _lookup(self, categories):
        """
            Look up if a category set is already in the compact set.
            return the index if so, return None otherwise
        """

        for idx, trial in enumerate(self.Set):

            # if the categories are not the same size, then they are 
            # not equal...
            #if len(categories) != len(trial['categories']): continue

            # check equality of all pairs of categories
            equals =[np.array_equal(*arrs) 
                     for arrs in zip(categories, trial['categories'])]

            # return index if all pairs are equal
            if all(equals): return idx

        # otherwise, return None
        return None


    def cat2ind(self,catlabel):
        category_list = ['Alpha','Beta','Gamma','Delta']
        treatAsBetas = [None,'Not-Alpha','Alpha']  #Legacy support        
        if catlabel in treatAsBetas:
            out = 1
        else:
            out = category_list.index(catlabel)                
        return out
    
    def add_frame(self, generation, task = 'generate'):
        """
        Add trials from a dataframe

        If task=='generate', then the dataframe must have columns:
                participant, trial, stimulus, categories

                If task=='assign', then the dataframe must have columns:
                participant, trial, stimulus, assignment, categories

        Where categories is a embedded list of known categories
        PRIOR to trial = 0.               
        """        
        if task == 'generate':
            for pid, rows in generation.groupby('participant'):
                for num, row in rows.groupby('trial'):
                    categories = row.categories.item()[:] #gotta copy the list with [:]                    
                    gen_exemplars = np.array(rows.loc[rows.trial<num, 'stimulus'].values)
                    if 'category' in rows.columns:                    
                        gen_cats = rows.loc[rows.trial<num, 'category'].values
                        for gen_cat in np.unique(gen_cats):
                            gen_idc = np.array([gi for gi, gc in enumerate(gen_cats) if gc == gen_cat])
                            categories += [gen_exemplars[gen_idc]]
                        add2cat = self.cat2ind(row.category.item())
                    else:
                        categories = row.categories.item() + [gen_exemplars]
                        add2cat = 1

                    genstim = row.stimulus.item()
                    stimulus = [genstim,add2cat]
                    if not 'wrap_ax' in row.columns:
                        wrap_ax = None
                    else:
                        wrap_ax = row.wrap_ax.item()
                    self.add(stimulus, categories = categories,participant = row.participant.item(),wrap_ax = wrap_ax)

        elif task == 'assign' or task == 'error':
            # So the response trials added here can be from any
            # category, not just the generated one
            for pid, rows in generation.groupby('participant'):
                #print pid
                for num, row in rows.groupby('trial'):
                    #categories don't grow in size here, so
                    #no + Bs
                    #print row.categories
                    categories = row.categories.item()
                    target = row.stimulus.item()
                    add2cat = row.assignment.item()
                    stimulus = [target,add2cat]
                    if not 'wrap_ax' in row.columns:
                        wrap_ax = None
                    else:
                        wrap_ax = row.wrap_ax.item()

                    self.add(stimulus, categories = categories,participant = row.participant.item(),wrap_ax=wrap_ax)
        else:
            raise ValueError('Oh no, it looks like you have specified an illegal value for the task argument!')

                
        return self
                
    
    def loglike(self, params, model, fixedparams = None, whole_array=False, parmxform = True,seedrng = False):
        """
        Evaluate a model object's log-likelihood on the
        trial set based on the provided parameters.
                
        If whole_array is True, then loglike returns the nLL
        of each trial in the Trialset. 
        """
        
        # reverse-transform parameter values
        if parmxform:
            params = model.parmxform(params, direction = -1)        

        # extract fixed parameters and feed it into params variable
        if hasattr(fixedparams,'keys'):
            #convert free parms to dict
            params = model.params2dict(params)
            for parmname in fixedparams.keys():
                params[parmname] = fixedparams[parmname]
        #Get stimsteps, if it doesn't exist, compute and add as property
        if hasattr(self,'stimstep'):
            stimstep = self.stimstep
        else:
            ndim = self.stimuli.shape[1]
            stimstep = []
            for di in range(ndim):
                uniques = np.unique(self.stimuli[:,di])
                st = uniques[1]-uniques[0]
                stimstep += [st]
        # iterate over trials
        loglike = 0
        ps_list = np.array([])
        if self.task is '':
            raise Exception('Task for trialset object not defined.')
        task = self.task
        for idx, trial in enumerate(self.Set):
            # format categories
            #170818 - uh oh, looks like this line doesn't correctly account for lists with [0]
            #Lists with [0] should be recognised as valid categories, and not empty
            #categories = [self.stimuli[i,:] for i in trial['categories'] if any(i)]
            categories = [self.stimuli[np.array(i,dtype=int),:] for i in trial['categories'] if len(i)>0] #Might want to find a faster way, avoiding the np.array dtype=int
            # Check if responseType is 1 (each element of response is strictly a new Beta) or 2 (elements of response correspond to categories)
            if hasattr(trial['response'][0], "__len__"):
                responseType = 2
                #Identify if any axis needs wrapping
                if not 'wrap_ax' in trial.keys():
                    #Legacy support. If trialset doesn't have wrap_ax, then no wrapping is required.
                    #This shouldn't really happen, but just in case
                    trial['wrap_ax'] = []
                    for category in range(len(trial['response'])):
                        trial['wrap_ax'] += [np.array([None for i in range(len(trial['response'][category]))])]
                    wraps = [None]
                else:
                    subwraps = np.array([])
                    for wrap in trial['wrap_ax']:
                        subwraps = np.append(subwraps,wrap)
                    wraps = np.unique(subwraps)
            else:
                responseType = 1
                #Identify if any axis needs wrapping
                if not 'wrap_ax' in trial.keys():
                    #Legacy support. If trialset doesn't have wrap_ax, then no wrapping is required.
                    trial['wrap_ax'] = np.array([None for i in range(len(trial['response']))])
                    wraps = [None]
                else:
                    wraps = np.unique(trial['wrap_ax'])
            #Iterate over axes wrappings
            for wrap in wraps:
                if task == 'generate':
                    # compute probabilities of generating exemplar in target cat
                    ##TO DO 030819 -- Correctly get the generations ps for each desired category (think add2cat)
                    if responseType == 1:
                        ps = model(categories, params, self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli, 1,self.task,seedrng = seedrng)
                        ps_idx = np.where(trial['wrap_ax']==wrap)[0]
                        #If it's a scalar, take it out of the array
                        if len(ps_idx)==1:
                            ps_idx = ps_idx[0]
                        ps_add = np.array(ps[trial['response'][ps_idx]])
                    elif responseType == 2:
                        ps_add = np.array([])
                        for category,resp in enumerate(trial['response']):
                            if len(resp)>0:
                                ps_idx = np.where(trial['wrap_ax'][category]==wrap)[0]
                                if len(ps_idx)>0: #Only bother where the desired wrap is relevant
                                    ps = model(categories, params, self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli, category,self.task,seedrng = seedrng)
                                    #If it's a scalar, take it out of the array
                                    if len(ps_idx)==1:
                                        ps_idx = ps_idx[0]
                                    respidx = np.array(resp[ps_idx],dtype=int)
                                    ps_add = np.append(ps_add,ps[respidx])
                            
                elif task=='assign':
                    if responseType==2 and len(trial['response'])>2:
                        raise Exception('Cannot handle assignment of multiple categories at this point.')
                    #Compute probabilities of assigning exemplar to cat 0
                    ps0 = model(categories, params, self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli, 0,self.task,seedrng = seedrng)
                    #Compute probabilities of assigning exemplar to cat 1
                    ps1 = model(categories, params,
                                self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli,
                                                                  1,self.task,seedrng = seedrng)


                    idc0 = trial['response'][0][np.where(trial['wrap_ax']==wrap)] #category 0
                    idc1 = trial['response'][1][np.where(trial['wrap_ax']==wrap)] #category 1

                    #ps_add = ps0[idc0]
                    ps_add = np.concatenate([ps0[idc0],ps1[idc1]])
                    #How about using binomial likelihoods instead?
                    #200218 SX: aahh, it gives the same values. Cool
                    # ps = []
                    # for i,ps_el in enumerate(ps0):
                    #         #find total assignments to category 0
                    #         ct0 = sum(np.array(idc0) == i)
                    #         #find total assignments to category 1
                    #         ct1 = sum(np.array(idc1) == i)
                    #         #total assignments overall
                    #         ctmax = ct0+ct1

                    #         ps += [ss.binom.pmf(ct0, ctmax,ps_el)]

                elif task=='error':
                    if responseType==2 and len(trial['response'])>2:
                        raise Exception('Cannot handle error prediction of multiple categories at this point.')
                    #For prediction of error probabilities, simply
                    #find the probability of classifying a
                    #stimulus as the wrong category
                    #There's something really wrong with how I'm doing things here.

                    #The old way (prior to 010618) was to simply treat cat 0 as
                    #correct and cat 1 as incorrect, since that's the way that the
                    #only error dataset NGPMG1994 has been set up. This is quite
                    #pointless, and I've generalised the code here so that it really
                    #looks at errors in categorising.
                    #ps = model(categories, params, self.stimrange).get_generation_ps(self.stimuli, 0,self.task)
                    #idc_err = trial['response'][0]
                    #Compute probabilities of assigning exemplar to cat 0
                    ps0 = model(categories, params,
                                self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli, 0,self.task,seedrng = seedrng)
                    #Compute probabilities of assigning exemplar to cat 1
                    ps1 = model(categories, params,
                                self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli, 1,self.task,seedrng = seedrng)
                    idc0 = trial['response'][0][trial['wrap_ax']==wrap]
                    idc1 = trial['response'][1][trial['wrap_ax']==wrap]
                    ps_add = np.concatenate([ps0[idc0],ps1[idc1]])

                    #190618 after much thought, error should be exactly the same as assign though...
                    #Actual category exemplars
                    correctcat = trial['categories']

                    correctps = []
                    wrongps   = []
                    #Iterate over each category
                    for i in range(len(correctcat)):
                        #Get right and wrong responses
                        correctresp = np.array([exemplar for exemplar in
                                                  trial['response'][i] if exemplar in
                                                  correctcat[i]])
                        wrongresp = np.array([exemplar for exemplar in
                                                  trial['response'][i] if not exemplar in
                                                  correctcat[i]])

                        #Get entire probability space
                        ps = model(categories, params,
                                   self.stimrange,stimstep=stimstep,wrap_ax=wrap).get_generation_ps(self.stimuli,
                                                                     i,self.task,seedrng = seedrng)
                        if len(correctresp)>0:
                            correctps = np.concatenate([correctps,ps[correctresp]])
                        if len(wrongresp)>0:
                            wrongps   = np.concatenate([wrongps,ps[wrongresp]])

                # check for nans and zeros
                if np.any(np.isnan(ps_add)):
                    ps_add = np.zeros(ps_add.shape)
                    # print categories
                    # print params
                    # print ps_add
                    # S = model.model  + ' returned NAN probabilities.'
                    # raise Exception(S)
                ps_add[ps_add<1e-308] = 1e-308
                if whole_array:
                    ps_list = np.append(ps_list,ps_add)
                else:
                    loglike += np.sum(np.log(ps_add))                        

        if whole_array:
            return -1.0 * np.log(ps_list)
        else:
            return -1.0 * loglike

    def correlate(self, params, model, alphas, fixedparams = None,seedrng = False):
        """Returns the correlation between model generation fit and observed
        participant error. This functions extracts the data for each individual
        participant in the trialset object, computes the observed error from that
        and calculates the model fit (negative LL) to that participant's data.        

        """
        from scipy.stats import stats as ss        
        ppts = self.participants
        ppt_err_rate = []
        ll = []
        for ppt in ppts:
            pptTrialObj = extractPptData(self.ppt)
            nresp = 0.0
            nresp_correct = 0.0
            for trial in pptTrialObj.Set:
                correctcats = trial['categories']
                #Iterate over each category
                for i,correctcat in enumerate(correctcats):
                    #update number of responses                    
                    nresp += len(trial['response'][i])
                    for correct in correctcat:
                        nresp_correct += trial['response'][i].count(correct)
            ppt_err_rate += [1-(nresp_correct/nresp)]
            #get the total ll of all permutations of the beta category
            ll += [pptTrialObj.loglike(params, model,seedrng=seedrng)]
        correlation = ss.pearsonr(ppt_err_rate,ll)

        
def hillclimber(model_obj, trials_obj, options, fixedparams = None, inits = None, results = True,callbackstyle='none', seed=None):
    """
    Run an optimization routine.

    model_obj is one of the model implementation in the module.
    init_params is a numpy array for the routine's starting location.
    trials_obj is a Trialset object.
    options is a dict of options for the routine. Example:
        method = 'Nelder-Mead',
        options = dict(maxiter = 500, disp = False),
        tol = 0.01,

    Function prints results to the console (if results is set to True), and returns the ResultSet
    object.
    """
    global currmodel
    currmodel = model_obj
    global currtrials
    currtrials = trials_obj
    global callback
    callback = callbackstyle
    global itcount
    global fitLL
    global seedrng    
    fitLL = True
    seedrng = seed
    # set initial params
    if inits is None:    
        inits = model_obj.rvs(fmt = list) #returns random parameters as list
        if results:
            print '\nStarting parms (randomly selected):'
            print inits
    #transform inits to be bounded within rules
    inits = model_obj.parmxform(inits, direction = 1)
    # run search
    itcount = 0
    if results:
        print 'Fitting: ' + model_obj.model
                
    res = op.minimize(    trials_obj.loglike, 
                inits, 
                args = (model_obj,fixedparams),
                callback = _callback_fun_, 
                **options
        )
    #reverse-transform the parms
    res.x = model_obj.parmxform(res.x, direction = -1)
        
    # print results
    if results:
        print '\n' + model_obj.model + ' Results:'
        print '\tIterations = ' + str(res.nit)
        print '\tMessage = ' + str(res.message)
        
        X = model_obj.params2dict(model_obj.clipper(res.x))
        for k, v in X.items():
            print '\t' + k + ' = ' + str(v) + ','
            
        print '\tLogLike = ' + str(res.fun)            
        AIC = funcs.aic(res.fun,len(inits))
        print '\tAIC = ' + str(AIC)
                        
    return res

def hillclimber_corr(model_obj, pptdata, tso, options, fixedparams = None, inits = None, results = True,callbackstyle='none',pearson=True):
    """
    Run an optimization routine that maximises correlations.

    model_obj is one of the model implementation in the module.
    pptdata is a dataframe containing information on each participant's error
    init_params is a numpy array for the routine's starting location.
    trials_obj is a Trialset object.
    options is a dict of options for the routine. Example:
        method = 'Nelder-Mead',
        options = dict(maxiter = 500, disp = False),
        tol = 0.01,

    Function prints results to the console (if results is set to True), and returns the ResultSet
    object.
    """
    global currmodel
    currmodel = model_obj
    global currpptdata
    currpptdata = pptdata
    global currtso
    currtso = tso
    global callback
    callback = callbackstyle
    global itcount
    global fitLL
    global seedrng
    fitLL = False
    execfile('Imports.py')
    import Modules.Funcs as funcs
    # set initial params
    if inits is None:    
        inits = model_obj.rvs(fmt = list) #returns random parameters as list
        if results:
            print '\nStarting parms (randomly selected):'
            print inits
    #transform inits to be bounded within rules
    inits = model_obj.parmxform(inits, direction = 1)
    # run search
    itcount = 0
    if results:
        print 'Fitting: ' + model_obj.model
                
    res = op.minimize(funcs.get_corr, 
                inits, 
                args = (pptdata,tso,model_obj,fixedparams,pearson),
                callback = _callback_fun_, 
                **options
        )
    #reverse-transform the parms
    res.x = model_obj.parmxform(res.x, direction = -1)
        
    # print results
    if results:
        print '\n' + model_obj.model + ' Results:'
        print '\tIterations = ' + str(res.nit)
        print '\tMessage = ' + str(res.message)
        
        X = model_obj.params2dict(model_obj.clipper(res.x))
        for k, v in X.items():
            print '\t' + k + ' = ' + str(v) + ','
            
        print '\tLogLike = ' + str(res.fun)            
        AIC = funcs.aic(res.fun,len(inits))
        print '\tAIC = ' + str(AIC)
                        
    return res


def _callback_fun_(xk):
    """
    Function executed at each step of the hill-climber
    If fitLL is true, it means regular hillclimber is running. Else, it's maximising correlations.
    """
    #callback = '.' #this line is here for easier manual switching of display
    global itcount
    global fitLL
    global seedrng
    if fitLL:
        model_obj,trials_obj,display = _fetch_global_(fitLL)
    else:
        model_obj,pptdata,tso,display = _fetch_global_(fitLL)
    #Set how many columns to print
    printcol = 20 
    if display is 'iter':
        if fitLL:
            fit = trials_obj.loglike(xk,model_obj,seedrng = seedrng)                
        else:
            execfile('Imports.py')
            import Modules.Funcs as funcs
            fit = funcs.get_corr(xk,pptdata,tso,model_obj,print_on=False) #220618 hmm not entirely sure if this works but can try
        xk = model_obj.parmxform(xk, direction = -1)
        print '\t[' + ', '.join([str(round(i,4)) for i in xk]) + '] f(x) = ' + str(round(fit,4))        
    elif display is '.':                
        if (np.mod(itcount,printcol)!=0) & (itcount>0):
            print '\b.',
            sys.stdout.flush()
        elif (itcount>0):
            print '\b.'

                        
                #print '\t[' + ', '.join([str(round(i,4)) for i in xk]) + ']'
    elif display is 'none':
        pass
    elif type(display) is str:
        if np.mod(itcount,printcol)==0 & itcount>0:
            eval('print ' + display)
        else:
            eval('print ' + '\b' +  display)
            

    itcount += 1


#Temporary function to enable printing of function value during callback of minimization
def _fetch_global_(fitLL=True):
    global currmodel
    global callback
    if fitLL:
        global currtrials
        return currmodel,currtrials,callback
    else:
        global currpptdata
        global currtso
        return currmodel,currpptdata,currtso,callback



def show_final_p(model_obj, trial_obj, params, show_data = False):
    #One final presentation of the set of probabilities for each stimulus
    task = trial_obj.task
    nstim = len(trial_obj.stimuli)
    for idx, trial in enumerate(trial_obj.Set):
        # format categories
        #categories = [trial_obj.stimuli[i,:] for i in trial['categories'] if any(i)]
        categories = [trial_obj.stimuli[i,:] for i in trial['categories'] if len(i)>0]
        ps0 = model_obj(categories, params, trial_obj.stimrange).get_generation_ps(trial_obj.stimuli, 0,trial_obj.task,seedrng = seedrng)
        ps1 = model_obj(categories, params, trial_obj.stimrange).get_generation_ps(trial_obj.stimuli, 1,trial_obj.task,seedrng = seedrng)
        
        
        if show_data is False:
            print 'Model Predictions:'
            dsize = int(np.sqrt(len(ps0)))
            print np.atleast_2d(ps0).reshape(dsize,-1)
            print np.atleast_2d(ps1).reshape(dsize,-1)
        else:                        
            dsize = int(np.sqrt(len(ps0)))
            cat0ct = []
            cat1ct = []
            cat0pt = []
            cat1pt = []
            
            responses = trial['response']                        
            for j in range(nstim):#max(responses[0])+1):
                cat0 = sum(np.array(responses[0])==j)
                cat1 = sum(np.array(responses[1])==j)
                catmaxct = cat0+cat1
                cat0ct += [cat0]
                cat1ct += [cat1]
                p0 = float(cat0)/float(catmaxct)
                p1 = 1-p0
                cat0pt += [p0]
                cat1pt += [p1]
                
                sse = sum((np.array(ps0)-np.array(cat0pt))**2 + \
                          (np.array(ps1)-np.array(cat1pt))**2)
                
                cat0pt = [round(i,4) for i in cat0pt]
                cat1pt = [round(i,4) for i in cat1pt]
                
                ps0 = [round(i,4) for i in ps0]
                ps1 = [round(i,4) for i in ps1]
                
                print 'Condition ' + str(idx)
                print 'SSE = ' + str(sse)
                print 'Model Predictions (Cat0):'
                print np.flipud(np.atleast_2d(ps0).reshape(dsize,-1))
                print 'Observed Data (Cat0):'
                print np.flipud(np.atleast_2d(cat0pt).reshape(dsize,-1))
                # print 'Model Predictions (Cat1):'
                # print np.flipud(np.atleast_2d(ps1).reshape(dsize,-1))
                # print 'Observed Data (Cat1):'
                # print np.flipud(np.atleast_2d(cat1pt).reshape(dsize,-1))
                
                #lll
                #print ps0
                #print ps1
                #print np.atleast_2d(ps0).reshape(4,4)
                #print np.atleast_2d(ps1).reshape(4,4)



# Extract participant-level data and particular unique trials
def extractPptData(trial_obj, ppt = 'all', unique_trials = 'all'):
    """
    Extracts data for a single participant (or range of participants, if it's a list)
    from a trialset object. Can also extract specific unique trials (aka
    trained category stimuli).
    
    If unique_trials is set to 'all', then all unique trials are included.
    
    Returns a trialset object
    """
    import copy as cp
    if ppt != 'all' and type(ppt) is not list:
        ppt = [ppt]        
    output_obj = cp.deepcopy(trial_obj)
    if unique_trials is not 'all':
        #check for the type of input
        if not hasattr(unique_trials,'__len__'):
            #scalars don't have this attr
            idx = unique_trials
        elif not hasattr(unique_trials[0],'__len__'):
            #if it's a list of scalars, extract only those
            idx = unique_trials
        else:
            #extract only trials that match these unique trials
            #Only handles one idx at a time for now 130218
            idx = trial_obj._lookup(unique_trials)
                        
        if idx is None:
            S = 'Specified set of unique trials not found in trial set.'
            raise Exception(S)
        #Remove all unique trials except the selected one
        if isinstance(idx,list):
            temp_obj = [chunk for i,chunk in enumerate(trial_obj.Set) if i in idx]
            output_obj.Set = []
            output_obj.Set = [chunk for chunk in temp_obj]
        else:
            temp_obj = trial_obj.Set[idx]                        
            output_obj.Set = []
            output_obj.Set.append(temp_obj)
    #Check responseType
    if hasattr(output_obj.Set[0]['response'][0], "__len__"):
        responseType = 2
    else:
        responseType = 1
        
    for ti,trialchunk in enumerate(output_obj.Set):        
        responsecats = trialchunk['response']
        pptcats = trialchunk['participant']
        wrapaxcats = trialchunk['wrap_ax']
        respList = np.array([])
        pptList = np.array([])
        wrapaxList = np.array([])
        if trial_obj.task is 'generate':
            if responseType==1:
                #convert pptcat and responsecat to array for easier indexing
                if ppt == 'all':
                    respList = np.array(responsecats)
                    pptList = np.array(pptcats)
                    wrapaxList = np.array(wrapaxcats)
                else:
                    for i in ppt:
                        extractIdx = np.array(pptcats==np.array(round(i)))
                        responsecats = np.array(responsecats)
                        pptcats = np.array(pptcats)
                        wrapaxcats = np.array(wrapaxcats)
                        respList = np.append(respList,responsecats[extractIdx])
                        pptList = np.append(pptList,pptcats[extractIdx])
                        wrapaxList = np.append(wrapaxList,wrapaxcats[extractIdx])
            elif responseType==2:
                ncategories = len(trialchunk['participant'])
                #iterate over categories of responses        
                respList = [np.array([], dtype = int) for _ in xrange(ncategories)]
                pptList = [np.array([], dtype = int) for _ in xrange(ncategories)]
                wrapaxList = [np.array([], dtype = int) for _ in xrange(ncategories)]        
                for pi,pptcat in enumerate(pptcats):
                    #convert pptcat and responsecat to array for easier indexing
                    responsecat = np.array(responsecats[pi])
                    pptcat = np.array(pptcats[pi])
                    wrapaxcat = np.array(wrapaxcats[pi])
                    if ppt == 'all':
                        respList[pi] = np.append(respList[pi],responsecat)
                        pptList[pi] = np.append(pptList[pi],pptcat)
                        wrapaxList[pi] = np.append(wrapaxList[pi],wrapaxcat)
                    else:
                        for i in ppt:
                            extractIdx = pptcat==round(i)
                            respList[pi] = np.append(respList[pi],responsecat[extractIdx])
                            pptList[pi] = np.append(pptList[pi],pptcat[extractIdx])
                            wrapaxList[pi] = np.append(wrapaxList[pi],wrapaxcat[extractIdx])
                
        elif trial_obj.task is 'assign' or trial_obj.task is 'error':
            #iterate over categories of responses        
            respList = [np.array([], dtype = int) for _ in xrange(ncategories)]
            pptList = [np.array([], dtype = int) for _ in xrange(ncategories)]
            wrapaxList = [np.array([], dtype = int) for _ in xrange(ncategories)]        
            for pi,pptcat in enumerate(pptcats):
                #convert pptcat and responsecat to array for easier indexing
                responsecat = np.array(responsecats[pi])
                pptcat = np.array(pptcats[pi])
                wrapaxcat = np.array(wrapaxcats[pi])
                if ppt == 'all':
                    respList[pi] = np.append(respList[pi],responsecat)
                    pptList[pi] = np.append(pptList[pi],pptcat)
                    wrapaxList[pi] = np.append(wrapaxList[pi],wrapaxcat)
                else:
                    for i in ppt:
                        extractIdx = pptcat==round(i)
                        respList[pi] = np.append(respList[pi],responsecat[extractIdx])
                        pptList[pi] = np.append(pptList[pi],pptcat[extractIdx])
                        wrapaxList[pi] = np.append(wrapaxList[pi],wrapaxcat[extractIdx])
        else:
            raise ValueError('trialset.task not specified. Please specify this as \'generate\' or \'assign\' in your script.')
        
        output_obj.Set[ti]['response'] = respList
        output_obj.Set[ti]['participant'] = pptList
        output_obj.Set[ti]['wrap_ax'] = wrapaxList
    #Clean up
    #cleanIdx = np.ones(len(output_obj.Set),dtype=bool)
    output_objTemp = cp.deepcopy(output_obj.Set)
    output_obj.Set = []
    for ti,trialchunk in enumerate(output_objTemp):
        if trial_obj.task is 'generate':
            if responseType==1:
                if len(trialchunk['participant'])>0:                        
                    #cleanIdx[ti] = False
                    output_obj.Set.append(trialchunk)
            elif responseType==2:
                size = 0
                for trialppt in trialchunk['participant']:
                    size += len(trialppt)
                if size>0:                        
                    #cleanIdx[ti] = False
                    output_obj.Set.append(trialchunk)
                    
        elif trial_obj.task is 'assign' or trial_obj.task is 'error':
            if len(trialchunk['participant'][0])>0:                        
                #cleanIdx[ti] = False
                output_obj.Set.append(trialchunk)

    #Finally, update the unique participant list
    if not ppt=='all':
        output_obj.participants = ppt
        output_obj.nparticipants = len(ppt)
        
    return output_obj

def loglike_allperm(params, model_obj, categories, stimuli, permute_category = 1,
                    fixedparams = None, task = 'generate',seedrng = False):
    """
    Finds the total loglikelihood of generating all permutations of some
    specified category. Default category to permute is 1 (i.e., the second category.)
    """
    if len(categories)>2:
        raise ValueError('This function can\'t deal with more than two',\
                    'categories yet. To fix this, go bug Xian or do it yourself.')

    import pandas as pd
    import math    
    cat2perm = categories[permute_category]
    cat2notperm = categories[1-permute_category]

    nstim = len(cat2perm)
    #condition and ppt numbers aren't important so just give it some arbitrary
    #value
    pptnum = 0;
    pptcondition = 'meh';
    # Get all permutations of cat2perm and make a new trialObj for it
    nbetapermute = math.factorial(nstim)
    raw_array = np.zeros((1,nbetapermute))
    #Iterate over the different permutations of to-be-permuted category
    for i, pexemplars in enumerate(funcs.permute(cat2perm)):
        pptDF = pd.DataFrame(columns = ['participant','stimulus','trial','condition','categories'])
        pptDF.stimulus = pd.to_numeric(pptDF.stimulus)
        pptTrialObj = Trialset(stimuli)
        pptTrialObj.task = task
        for trial,exemplar in enumerate(pexemplars):
                pptDF = pptDF.append(
                        dict(participant=pptnum, stimulus=exemplar, trial=trial, condition=pptcondition, categories=[cat2notperm]),ignore_index = True
                )
        pptTrialObj.add_frame(pptDF)
        raw_array_ps = pptTrialObj.loglike(params,model_obj,seedrng = seedrng)
        raw_array[:,i] = raw_array_ps
    #Compute the total likelihood as the sum of the likelihood of each
    #permutation. Since I don't know an easy way to add something which is in
    #log-form, I'll convert it to exp first. However, the neg loglikelihoods can
    #get really large, which will tip it over to Inf when applying exp. To get
    #around this, subtract the LL by some constant (e.g., its max), exp it, add
    #up the probabilities, then log, and add it to the log of the constant
    raw_array_max = raw_array.max()
    raw_array_t = np.exp(-(raw_array - raw_array_max)).sum()
    raw_array_ll = -np.log(raw_array_t) + raw_array_max
    return raw_array_ll


# def add_model_data():
#         #Temporary code to add model parm names to gs results
#         import re
#         import os
#         import pickle

#         pickledir = 'pickles/'
#         prefix = 'gs_'
#         #Compile regexp obj
#         allfiles =  os.listdir(pickledir)
#         r = re.compile(prefix)
#         gsfiles = filter(r.match,allfiles)

#         for i,file in enumerate(gsfiles):
#                 with open(pickledir+file,'rb') as f:
#                         fulldata = pickle.load(f)
#                 modelnames = fulldata.keys()
#                 for j in modelnames:
#                         #Add data on their model type
#                         if j == 'Hierarchical Sampling':
#                                 fulldata[j]['parmnames'] = ['category_mean_bias',
#                                                             'category_variance_bias',
#                                                             'domain_variance_bias',
#                                                             'determinism']
#                         elif j == 'Copy and Tweak':
#                                 fulldata[j]['parmnames'] = ['specificity',
#                                                             'determinism']
#                         elif j == 'PACKER':
#                                 fulldata[j]['parmnames'] =  ['specificity',
#                                                              'tradeoff',
#                                                              'determinism']
#                 with open(pickledir+file,'wb') as f:
#                         pickle.dump(fulldata,f)
                                

# def print_gs_nicenice():
#         #Find all gs fits and print them. Nice nice.        
#         import re
#         import os
#         import pickle
        
#         pickledir = 'pickles/'
#         prefix = 'gs_'
#         #Compile regexp obj
#         allfiles =  os.listdir(pickledir)
#         r = re.compile(prefix)
#         gsfiles = filter(r.match,allfiles)

#         for i,file in enumerate(gsfiles):
#                 #Extract key data from each file
#                 print '\n' + file
#                 print '------'
#                 with open(pickledir+file,'rb') as f:
#                         fulldata = pickle.load(f)
#                 modelnames = fulldata.keys()
#                 for j in modelnames:
#                         print 'Model:' + j
#                         for pi,pname in enumerate(fulldata[j]['parmnames']):
#                                 print '\t' + pname + ': ' + str(fulldata[j]['bestparmsll'][pi])
#                         print '\tLogLike' + ' = ' + '-' + str(fulldata[j]['bestparmsll'][pi+1])
#                         print '\tAIC'  + ' = ' + str(fulldata[j]['bestparmsll'][pi+2])


