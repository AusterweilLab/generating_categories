#####
# This submodule contains custom code to fit the modules to datasets.
# it is not written to be very general and I edit it a lot!
#####

import scipy.optimize as op
import numpy as np
import sys


def _callback_fun_(xk):
	"""
	Function executed at each step of the hill-climber
	"""
	# print '\t[' + ', '.join([str(round(i,4)) for i in xk]) + ']'
	print '\b.',
	sys.stdout.flush()


def costfun(params, model_obj, dataset, stimuli):
	"""
	Evaluate the fit of parameters to all trials in a dataset.

	params is an array-like of parameters for the model
	model_obj is a model class object
	dataset is a list of trial dicts. Each item must contain:
		'categories': a list of numpy arrays
		'response': the integer row number of the stimulus generated
	stimuli is a numpy array of generation candidates

	function returns the negative log likelihood (lower = better).
	"""

	# iterate over trials
	ps = np.zeros(len(dataset))
	for i, trial in enumerate(dataset):
		
		obj = model_obj(trial['categories'], params)
		predictions = obj.get_generation_ps(stimuli, 1)
		ps[i] = predictions[trial['response']]

	# check for NaN
	if np.any(np.isnan(ps)):
		raise Exception('You got nan probabilities. Sorry :-(')

	# remove zeros to prevent infs
	ps[ps<1e-308] = 1e-308

	lps = np.log(ps)
	loglike = np.sum(lps)
	return -1.0 * loglike


def hillclimber(model_obj, init_params, dataset, stimuli, options):
	"""
	Run an optimization routine.

	model_obj is one of the model implementation in the module.
	init_params is a numpy array for the routine's starting location.
	dataset is a list of trials being fitted. each trial is a dict contianing:
		'categories': a list of numpy arrays
		'response': the integer row number of the stimulus generated
	stimuli is a numpy array of all the stimuli in the space
	options is a dict of options for the routine. Example:
		method = 'Nelder-Mead',
		options = dict(maxiter = 500, disp = False),
		tol = 0.01,

	Function prints results to the console, and returns the ResultSet
	object.
	"""

	# run search
	print '\nFitting: ' + model_obj.model
	res = op.minimize(
		costfun, init_params, 
		args = (model_obj, dataset, stimuli),
		callback = _callback_fun_, **options
	)

	# print results
	print '\n' + model_obj.model + ' Results:'
	print '\tIterations = ' + str(res.nit)
	print '\tMessage = ' + str(res.message)

	final_obj = model_obj(None, res.x)
	for k in final_obj.parameter_names:
		v = getattr(final_obj, k)
		print '\t' + k + ' = ' + str(v) + ','
	print '\tLogLike = ' + str(res.fun)

	AIC = 2.0*len(init_params) - 2.0* (-1.0 * res.fun)
	print '\tAIC = ' + str(AIC)

	return res