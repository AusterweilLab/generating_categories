import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Model

class Packer(Model):
	"""
	Exemplar similarity implementation of the packing model.
	"""

	model = 'PACKER'
	parameter_names = [
		'specificity', # c > 0 
		'between',  # phi, any real
		'within', # gamma, any real
		'determinism' # theta > 0
	] 

	@staticmethod
	def rvs():
		params = [
			np.random.uniform(0.1, 6.0), # specificity
			np.random.uniform(-6.0, 0.0), # between. biased negative.
			np.random.uniform(0.0, 6.0), # within. biased positive
			np.random.uniform(0.1, 6.0) # determinism
		]
		return params

	def _param_handler_(self):
		super(Packer, self)._param_handler_()
		if self.specificity <= 0: self.specificity = 1e-10
		if self.determinism <= 0: self.determinism = 1e-10


	def _get_ss(self, X, Y, param = 1.0):
		""" 
		function to compute summed similarity along rows of 
		X across all items in Y. Resulting array will have one element 
		per row of X.
		"""
		distance   = Funcs.pdist(np.atleast_2d(X), np.atleast_2d(Y), w = self.wts)
		similarity = np.exp(-float(self.specificity) * distance)
		similarity = similarity * float(param)
		return np.sum(similarity, axis = 1)


	def get_generation_ps(self, stimuli, category):

		# compute contrast sum similarity
		contrast_examples   = self.exemplars[self.assignments != category]
		contrast_ss   = self._get_ss(stimuli, contrast_examples, param = self.between)

		# compute target sum similarity
		target_examples = self.exemplars[self.assignments == category]
		target_ss   = self._get_ss(stimuli, target_examples, param = self.within)

		# aggregate target and contrast similarity
		total = contrast_ss + target_ss

		# nan out members of the target category
		if any(self.assignments == category):
			known_members = Funcs.intersect2d(stimuli, target_examples)
			total[known_members] = np.nan

		ps = Funcs.softmax(total, theta = self.determinism)
		return ps

