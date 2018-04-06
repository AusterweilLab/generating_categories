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
	def model(): pass

	@abc.abstractproperty
	def parameter_names(): pass

	@abc.abstractproperty
	def parameter_rules(): pass

	@abc.abstractmethod
	def _make_rvs(): pass

	@classmethod
	def rvs(cls, fmt = dict, **kwargs):
		"""
		return random parameters in dict or list format
		"""

		params = cls._make_rvs(**kwargs)

		if fmt not in [dict, list]:
			raise Exception('fmt must be dict or list.')
		
		if fmt == list: 
			return params
		else: 
			return dict(zip(cls.parameter_names, params))

	@classmethod
	def clipper(cls, params):
		"""
		Clip a set of parameters according to model rules.
		Return data in the same format it arrived.
		"""

		# format as list for now
		if not isinstance(params, dict):
			param_dict = cls.params2dict(params)
		else: param_dict = dict(params)

		# clip dict
		for k, rules in cls.parameter_rules.items():
			if rules is None: continue
                        if not param_dict.has_key(k): continue
			if 'min' in rules.keys():
				if param_dict[k] < rules['min']:
					param_dict[k] = rules['min']
			if 'max' in rules.keys():
				if param_dict[k] > rules['max']:
					param_dict[k] = rules['max']

		# return in original format
		if not isinstance(params, dict):
			return [param_dict[k] for k in cls.parameter_names]
		else: 
			return param_dict


        @classmethod
        def parmxform(cls, params, direction = 1):
                """
                Transform a set of parameters according to model rules.                
                """
                toggle = True #make it a little easier to switch this on or off
                if toggle:
		        if not isinstance(params, dict):
			        param_dict = cls.params2dict(params)
		        else: param_dict = dict(params)
                        
                        for k, rules in cls.parameter_rules.items():
                                gotmin = False
                                gotmax = False
                                min = 0
                                max = 0
                                if rules is None:
                                        continue
                                if 'min' in rules.keys():
                                        gotmin = True
                                        min = rules['min']
                                if 'max' in rules.keys():
                                        gotmax = True
                                        max = rules['max']
                                if gotmin and gotmax:
                                        #Do logit transform scaled to min and max
                                        param_dict[k] = Funcs.logit_scale(param_dict[k],min,max,direction = direction)
                                elif gotmin:
                                        #Do log transform
                                        param_dict[k] = Funcs.log_scale(param_dict[k],min,direction = direction)

		        # return in original format
		        if not isinstance(params, dict):
			        return [param_dict[k] for k in cls.parameter_names]
		        else: 
			        return param_dict
                else:
                        return params
                                
                                
	@classmethod
	def params2dict(cls, params):
		"""
		Convert list parameters to dict, assuming order set by
		parameter_names. Raises exception if there are not 
		enough params (or too many).
		"""

		if len(params) != len(cls.parameter_names):
			S = 'Not enough (or too many) parameters!\nRequired:'
			S += ''.join(['\n\t' + i  for i in cls.parameter_names])
			raise Exception(S)
		return dict(zip(cls.parameter_names, params))
		

	@abc.abstractmethod
	def get_generation_ps(self, stimuli, category): pass

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
			params = self.params2dict(params)

		# clip parameters into allowed range
		params = self.clipper(params)

		# assign descriptives
		self.categories = [np.atleast_2d(i) for i in categories]
		self.nfeatures = self.categories[0].shape[1]
		self.params = params

		# setup functions
		self._param_handler_()
		self._wts_handler_()
		self._update_()


	def __str__(self):
			S = self.model + ' Model. Current state:' 
			for k in self.parameter_names:
				S += '\n\t' + k + ' = ' + str(getattr(self, k))
			for j in range(self.ncategories):
				S += '\n\t' + 'Category ' +  str(j) + ': ' 
				S += str(self.nexemplars[j]) + ' examples.'
			return S + '\n'

	def _param_handler_(self):
		""" 
		Ensures all the right parameters are in place, and creates
		class attributes based on values.
		"""
		for k in self.parameter_names:
			if k not in self.params.keys():
				raise Exception("There is no '" + k + "' parameter!!!")
			else: 
				setattr(self, k, self.params[k])

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
                        #print sum(ps)-1
			num = Funcs.wpick(ps)
			values = np.atleast_2d(stimuli[num,:])

			# add the item to the category
                        if num != None:
                                generated_examples.append(num)
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
