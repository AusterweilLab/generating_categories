import abc
import numpy as np

# imports from module
import utils


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
		
		# assign descriptives
		self.categories = [np.atleast_2d(i) for i in categories]
		self.nfeatures = self.categories[0].shape[1]
		self.params = params

		# setup functions
		self._param_handler_()
		self._update_()


	def __str__(self):
			S = self.model + ' Model. Current state:' 

			for k in self.parameter_names:
				S += '\n\t' + k + ' = ' + str(getattr(self, k))

			for j in range(self.ncategories):
				S += '\n\t' + 'Category ' +  str(j) + ': ' 
				S += str(self.nexemplars[j]) + ' examples.'

			return S + '\n'


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


	def _params_to_dict_(self, params):
		"""
		Convert list parameters to dict, assuming order set by
		self.parameter_names
		"""

		# make sure all parameters are there.
		if len(params) != len(self.parameter_names):
			S = 'Not enough (or too many) parameters!\nRequired:'
			S += ''.join(['\n\t' + i  for i in self.parameter_names])
			raise Exception(S)
		return dict(zip(self.parameter_names, params))


	def _update_(self):
		"""
		Generate descriptives about the known categories. 
		The fields defined below change when items are generated or fotgotten,
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
		Simulate the generation of nexemplars, sourced from stimuli, into a category.
		The resulting category will be added to the model's memory, and the identity 
		of the generated iutems wilol be returned.
		"""

		if nexemplars is None:
			nexemplars = sum(self.nexemplars)

		# open up the new category
		self.categories.append(np.empty((0, self.nfeatures)))

		# iterate over examples
		generated_examples = []
		for i in range(nexemplars):

			# compute probabilities, then pick an item
			ps = self.get_generation_ps(stimuli, category)
			num = utils.wpick(ps)
			values = np.atleast_2d(stimuli[num,:])
			generated_examples.append(num)

			# add the item to the category
			self.categories[-1] = np.concatenate(
				[self.categories[-1], values], 
				axis = 0)

			# update knowledge
			self._update_()

		return generated_examples


	@abc.abstractmethod
	def get_generation_ps(self, stimuli, category):
		"""
		Function to return probability of generating 'stimuli' into
		'category', given the model's current state.
		"""
		pass