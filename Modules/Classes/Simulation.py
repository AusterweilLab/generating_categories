import scipy.optimize as op
import numpy as np
import sys

import Modules.Funcs as Funcs

currmodel='' #temp
currtrials=''


class Trialset(object):

	"""
	A class representing a collection of trials
        Data (i.e., responses) is saved in a list Set
	"""
        
	def __init__(self, stimuli):
		
		# figure out what the stimulus domain is
		self.stimuli = stimuli

		# initialize trials list
		self.Set = [] # compact set
		self.nunique = 0
		self.nresponses = 0
                self.task = ''
                
	def __str__(self):
		S  = 'Trialset containing: ' 
		S += '\n\t ' + str(self.nunique) + ' unique trials '
		S += '\n\t ' + str(self.nresponses) + ' total responses'
                # S += '\nTask: ' + self.task
		return S

	def _update(self):
		self.nunique = len(self.Set)
		self.nresponses = sum([len(i['response']) for i in self.Set])

	def add(self, response, categories = []):
		"""Add a single trial to the trial lists
                
                If response variable is a scalar, then add response to only one
                category. If response variable is a 2-element list, then add the
                value of the first element to the category specified by the
                second element.

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
                
		# sort category lists, do a lookup
		categories = [np.sort(i) for i in categories]
		idx = self._lookup(categories)

		# if there is no existing configuration, add a new one
		if idx is None:
			self.nunique += 1
                        if responseType == 1:
			        self.Set.append(dict(
				        response = [response], 
				        categories = categories)
			        )
                        elif responseType == 2:
                                ncat = len(categories)                             
                                respList =  [[] for _ in xrange(len(categories))]
                                #respList[add2cat] = np.append(respList[add2cat],(response))
                                respList[add2cat].append(response)
			        self.Set.append(dict(
				        response = respList,
				        categories = categories)
			        )

		# if there is an index, just add the response
		else:
                        if responseType == 1:
			        self.Set[idx]['response'] = np.append(
				        self.Set[idx]['response'], response)
                        elif responseType == 2:
                                self.Set[idx]['response'][add2cat].append(response)
                                #self.Set[idx]['response'][add2cat] = np.append(
                                #        self.Set[idx]['response'][add2cat],response)
                                #Hmm, why can't I just use self.Set[idx]['response']...
                                #...[add2cat].append(response)?
                                

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
			if len(categories) != len(trial['categories']): continue

			# check equality of all pairs of categories
			equals =[	np.array_equal(*arrs) 
					for arrs in zip(categories, trial['categories'])]

			# return index if all pairs are equal
			if all(equals): return idx

		# otherwise, return None
		return None


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
				        Bs = rows.loc[rows.trial<num, 'stimulus'].as_matrix()
				        categories = row.categories.item() + [Bs]
				        stimulus = row.stimulus.item()
                                        self.add(stimulus, categories = categories)

                elif task == 'assign':
                        # So the response trials added here can be from any
                        # category, not just the generated one
                        for pid, rows in generation.groupby('participant'):
                                for num, row in rows.groupby('trial'):
                                        #categories don't grow in size here, so
                                        #no + Bs
                                        #print row.categories
                                        categories = row.categories.item()
                                        target = row.stimulus.item()
                                        add2cat = row.assignment.item()
                                        stimulus = [target,add2cat]
                                        self.add(stimulus, categories = categories)
                else:
                        raise ValueError('Oh no, it looks like you have specified an',\
                                         'illegal value for the task argument!')

                
                return self
                

	def loglike(self, params, model):
		"""
			Evaluate a model object's log-likelihood on the
			trial set based on the provided parameters.
		"""

		# iterate over trials
		loglike = 0
                task = self.task
		for idx, trial in enumerate(self.Set):

			# format categories
			categories = [self.stimuli[i,:] for i in trial['categories'] if any(i)]
                        

                        # if it's an assignment task, also compute probabilities for other category (cat0)
                        # ps0 = np.zeros(ps1.shape)
                        if task is 'generate':                                
			        # compute probabilities of generating exemplar in cat 1
			        ps = model(categories, params).get_generation_ps(self.stimuli, 1,self.task)
                                ps = ps[trial['response']]
                        elif task=='assign':
                                #Compute probabilities of assigning exemplar to cat 0
                 		ps0 = model(categories, params).get_generation_ps(self.stimuli, 0,self.task)
                                #Compute probabilities of assigning exemplar to cat 1
                                ps1 = model(categories, params).get_generation_ps(self.stimuli, 1,self.task)
                                idc0 = trial['response'][0]
                                idc1 = trial['response'][1]
                                ps = np.concatenate([ps0[idc0],ps1[idc1]])
                                        
                                
                                # ps0 = model(categories, params).get_generation_ps(self.stimuli, 0,self.task)
                                # #emergency coding - convert indices to int
                                # #emconv0 = trial['response'][0]
                                # #emconv1 = trial['response'][1]
                                # #emint0 = [ int(x) for x in emconv0 ]
                                # #emint1 = [ int(x) for x in emconv1 ]
                                # #ps = ps1[trial['response'][0]] + ps0[trial['response'][1]]
                                # idc0 = trial['response'][0]
                                # idc1 = trial['response'][1]
                                # ps = np.concatenate([ps1[idc0],ps0[idc1]])



			# check for nans and zeros
			if np.any(np.isnan(ps)):
				S = model.model  + ' returned NAN probabilities.'
				raise Exception(S)
			ps[ps<1e-308] = 1e-308
                        
			loglike += np.sum(np.log(ps))
                        
                        
		return -1.0 * loglike


def hillclimber(model_obj, trials_obj, options, inits = None):
	"""
	Run an optimization routine.

	model_obj is one of the model implementation in the module.
	init_params is a numpy array for the routine's starting location.
	trials_obj is a Trialset object.
	options is a dict of options for the routine. Example:
		method = 'Nelder-Mead',
		options = dict(maxiter = 500, disp = False),
		tol = 0.01,

	Function prints results to the console, and returns the ResultSet
	object.
	"""
        global currmodel
        currmodel = model_obj
        global currtrials
        currtrials = trials_obj
        
	# set initial params
	if inits is None:	
		inits = model_obj.rvs(fmt = list) #returns random parameters as list
        print 'Starting parms:'
        print inits
	# run search
	print '\nFitting: ' + model_obj.model
	res = op.minimize(	trials_obj.loglike, 
				inits, 
				args = (model_obj),
				callback = _callback_fun_, 
				**options
        )

	# print results
	print '\n' + model_obj.model + ' Results:'
	print '\tIterations = ' + str(res.nit)
	print '\tMessage = ' + str(res.message)

	X = model_obj.params2dict(model_obj.clipper(res.x))
	for k, v in X.items():
		print '\t' + k + ' = ' + str(v) + ','
	print '\tLogLike = ' + str(res.fun)

	AIC = 2.0*len(inits) - 2.0* (-1.0 * res.fun)
	print '\tAIC = ' + str(AIC)

	return res

def _callback_fun_(xk):
	"""
	Function executed at each step of the hill-climber
	"""
        #model_obj,trials_obj = _fetch_global_()
        #ll = trials_obj.loglike(xk,model_obj)                
        #print '\t[' + ', '.join([str(round(i,4)) for i in xk]) + '] f(x) = ' + str(round(ll,4))
        #print '\t[' + ', '.join([str(round(i,4)) for i in xk]) + ']'
	print '\b.',
	sys.stdout.flush()

#Temporary function to enable printing of function value during callback of minimization
def _fetch_global_():
        global currmodel
        global currtrials
        return currmodel,currtrials


def show_final_p(model_obj, trial_obj, params, show_data = False):
        #One final presentation of the set of probabilities for each stimulus        
        for idx, trial in enumerate(trial_obj.Set):
                # format categories
	        categories = [trial_obj.stimuli[i,:] for i in trial['categories'] if any(i)]
                
                ps1 = model_obj(categories, params).get_generation_ps(trial_obj.stimuli, 1,trial_obj.task)
                ps0 = model_obj(categories, params).get_generation_ps(trial_obj.stimuli, 0,trial_obj.task)

                if show_data is False:
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
                        for j in range(16):#max(responses[0])+1):
                                cat0 = sum(np.array(responses[0])==j)
                                cat1 = sum(np.array(responses[1])==j)
                                catmaxct = cat0+cat1
                                cat0ct += [cat0]
                                cat1ct += [cat1]
                                p0 = float(cat0)/float(catmaxct)
                                p1 = 1-p0
                                cat0pt += [p0]
                                cat1pt += [p1]

                        cat0pt = [round(i,4) for i in cat0pt]
                        cat1pt = [round(i,4) for i in cat1pt]

                        ps0 = [round(i,4) for i in ps0]
                        ps1 = [round(i,4) for i in ps1]
                                
                        print np.flipud(np.atleast_2d(ps0).reshape(dsize,-1))
                        print np.flipud(np.atleast_2d(cat0pt).reshape(dsize,-1))
                        print np.flipud(np.atleast_2d(ps1).reshape(dsize,-1))
                        print np.flipud(np.atleast_2d(cat1pt).reshape(dsize,-1))

                #lll
                #print ps0
                #print ps1
                #print np.atleast_2d(ps0).reshape(4,4)
                #print np.atleast_2d(ps1).reshape(4,4)

