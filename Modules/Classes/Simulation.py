import scipy.optimize as op
import numpy as np
import sys

import Modules.Funcs as Funcs


class Trialset(object):

	"""
	A class representing a collection of trials
	"""

	def __init__(self, stimuli):
		
		# figure out what the stimulus domain is
		self.stimuli = stimuli

		# initialize trials list
		self.Set = [] # compact set
		self.nunique = 0
		self.nresponses = 0

	def __str__(self):
		N = len(self.Set)
		S  = 'Trialset containing: ' 
		S += '\n\t ' + str(self.nunique) + ' unique trials '
		S += '\n\t ' + str(self.nresponses) + ' total responses'
		return S

	def add(self, response, categories = []):
		"""
			Add a single trial to the trial lists
		"""

		# sort category lists, do a lookup
		categories = [np.sort(i) for i in categories]
		idx = self._lookup(categories)

		# if there is no existing configuration, add a new one
		if idx is None:
			self.nunique += 1
			self.Set.append(dict(
				response = [response], 
				categories = categories)
			)

		# if there is an index, just add the response
		else:
			self.Set[idx]['response'] = np.append(
				self.Set[idx]['response'], response)

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


	def add_frame(self, generation):
		"""
			Add trials from a generation dataframe with columns:
					participant, trial, stimulus, categories

			Where categories is a embedded list of known categories
			PRIOR to trial = 0.
		""" 

		for pid, rows in generation.groupby('participant'):
			for num, row in rows.groupby('trial'):

				Bs = rows.loc[rows.trial<num, 'stimulus'].as_matrix()
				categories = row.categories.item() + [Bs]
				stimulus = row.stimulus.item()
				self.add(stimulus, categories = categories)
		return self

	def loglike(self, params, model):
		"""
			Evaluate a model object's log-likelihood on the
			trial set based on the provided parameters.
		"""

		# iterate over trials
		loglike = 0
		for idx, trial in enumerate(self.Set):

			# format categories
			categories = [self.stimuli[i,:] for i in trial['categories'] if any(i)]

			# compute probabilities
			ps = model(categories, params).get_generation_ps(self.stimuli, 1)
			ps = ps[trial['response']]

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

	# set initial params
	if inits is None:	
		inits = model_obj.rvs(fmt = list)

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

	for k, v in zip(model_obj.parameter_names, res.x):
		print '\t' + k + ' = ' + str(v) + ','
	print '\tLogLike = ' + str(res.fun)

	AIC = 2.0*len(inits) - 2.0* (-1.0 * res.fun)
	print '\tAIC = ' + str(AIC)

	return res


def _callback_fun_(xk):
	"""
	Function executed at each step of the hill-climber
	"""
	# print '\t[' + ', '.join([str(round(i,4)) for i in xk]) + ']'
	print '\b.',
	sys.stdout.flush()
