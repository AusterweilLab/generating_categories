import abc
import numpy as np

# imports from module
import Modules.Funcs as Funcs


class Model(object):
	"""		
	Abstract base class. This is the starting point for all concrete models.
	"""
	
	__metaclass__ = abc.ABCMeta

	@abc.abstractproperty
	def model(self):
		pass

	@abc.abstractproperty
	def parameter_names(self):
		pass

	@abc.abstractmethod
	def rvs():
		"""	Static method to generate random parameters. """
		pass

	@abc.abstractmethod
	def _param_handler_(self):
		""" 
		Ensures all the right parameters are in place, and creates
		class attributes based on values.

		Models must add custom logic to ensure values lie within 
		the allowed range.
		"""
		for k in self.parameter_names:
			if k not in self.params.keys():
				raise Exception("There is no '" + k + "' parameter!!!")
			else:
				setattr(self, k, self.params[k])

	@abc.abstractmethod
	def get_generation_ps(self, stimuli, category):
		"""
		Function to return probability of generating 'stimuli' into
		'category', given the model's current state.
		"""
		pass


	def __init__(self, categories, params):
		"""
			Initialize the model. "categories" should be a list of numpy
			arrays with the same number of columns (features). Items in 
			"categories" can have unequal number of rows (examples).

			'params' is a dict containing all model parameters. 'params'
			should contain an entry for each of the items defined by the 
			'parameter_names' attribute of the concrete class
		"""
		
		# force params to dict if it is not one
		if not isinstance(params, dict):
			params = self._params_to_dict_(params)
		
		# create dummy object if needed
		if categories is None:
			print 'Warning: creating a dummy Model.'
			self.params = params
			self.ncategories, self.nfeatures = 0, 0
			self._param_handler_()
			self._reset_param_dict_()
			return

		# assign descriptives
		self.categories = [np.atleast_2d(i) for i in categories]
		self.nfeatures = self.categories[0].shape[1]
		self.params = params

		# setup functions
		self._param_handler_()
		self._wts_handler_()
		self._reset_param_dict_()
		self._update_()


	def __str__(self):
			S = self.model + ' Model. Current state:' 
			for k in self.parameter_names:
				S += '\n\t' + k + ' = ' + str(getattr(self, k))
			for j in range(self.ncategories):
				S += '\n\t' + 'Category ' +  str(j) + ': ' 
				S += str(self.nexemplars[j]) + ' examples.'
			return S + '\n'


	def _wts_handler_(self):
		"""
			Sets feature weight parameters for models.
			Raises exception if wts is not the right size.
		"""

		if 'wts' not in self.params.keys():
			self.wts = np.ones(self.nfeatures) / self.nfeatures
			return

		if len(self.params['wts']) != self.nfeatures:
			raise Exception("Invalid wts parameter!")

		wts = np.array(self.params['wts'])
		self.wts = wts / float(np.sum(wts))
		self.params['wts'] = self.wts


	def _reset_param_dict_(self):
		"""
			Resets self.params given updated values.
		"""
		for k in self.params.keys():
			self.params[k] = getattr(self, k)

	def _params_to_dict_(self, params):
		"""
		Convert list parameters to dict, assuming order set by
		self.parameter_names. Raises exception if there are not 
		enough params.
		"""

		if len(params) != len(self.parameter_names):
			S = 'Not enough (or too many) parameters!\nRequired:'
			S += ''.join(['\n\t' + i  for i in self.parameter_names])
			raise Exception(S)
		return dict(zip(self.parameter_names, params))


	def _update_(self):
		"""
		Generate descriptives about the known categories. 
		The fields defined below change when items are generated or forgotten,
		so this function is called whenever there is a change to model memory.
		"""
		self.ncategories = len(self.categories)
		self.nexemplars = np.array([i.shape[0] for i in self.categories])
		self.exemplars = np.concatenate(self.categories, axis = 0)
		self.assignments = []
		for i in range(self.ncategories):
			self.assignments += [i] * self.nexemplars[i]
		self.assignments = np.array(self.assignments)


	def forget_category(self, category):
		""" Delete an category from the model's memory """
		self.categories.pop(category)
		self._update_()
		

	def simulate_generation(self, stimuli, category, nexemplars = None):
		"""
		Simulate the generation of n-exemplars, sourced from stimuli, into a category.
		The resulting category will be added to the model's memory, and the identity 
		of the generated items will be returned.
		"""

		if nexemplars is None:
			nexemplars = sum(self.nexemplars)

		# open up the new category if needed
		if category >= self.ncategories:
			self.categories.append(np.empty((0, self.nfeatures)))

		# iterate over examples
		generated_examples = []
		for i in range(nexemplars):

			# compute probabilities, then pick an item
			ps = self.get_generation_ps(stimuli, category)
			num = Funcs.wpick(ps)
			values = np.atleast_2d(stimuli[num,:])
			generated_examples.append(num)

			# add the item to the category
			self.categories[category] = np.concatenate(
				[self.categories[category], values], 
				axis = 0)

			# update knowledge
			self._update_()

		return generated_examples



class Exemplar(Model):
	"""		
	Abstract base class for Exemplar models. Basically this is used to add 
	a function computing summed similarity.
	"""
	__metaclass__ = abc.ABCMeta

	def _sum_similarity(self, X, Y, 
		param = 1.0,	
		wts  = None, 
		c = None ):
		""" 
		function to compute summed similarity along rows of 
		X across all items in Y. Resulting array will have one element 
		per row of X.

		the "param" argument acts as a multiplier for similarities prior to summation
		"c" and "wts" can be arbitrary if supplied, or based on the model attribute if not
		"""

		# set weights and c
		if wts is None: wts = self.wts
		if c is None: c = self.specificity

		distance   = Funcs.pdist(np.atleast_2d(X), np.atleast_2d(Y), w = wts)
		similarity = np.exp(-float(c) * distance)
		similarity = similarity * float(param)
		return np.sum(similarity, axis = 1)