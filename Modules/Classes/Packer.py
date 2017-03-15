import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Exemplar

class Packer(Exemplar):
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
	def rvs(fmt = dict):
		"""
		Return random parameters in dict or list format.
		"""
		params = [
			np.random.uniform(0.1, 6.0), # specificity
			np.random.uniform(-6.0, 0.0), # between. biased negative.
			np.random.uniform(0.0, 6.0), # within. biased positive
			np.random.uniform(0.1, 6.0) # determinism
		]

		if fmt not in [dict, list]:
			raise Exception('Format must be dict or list.')

		if fmt == list:
			return params
		else:
			return dict(zip(Packer.parameter_names, params))


	def _param_handler_(self):
		super(Packer, self)._param_handler_()
		if self.specificity <= 0: self.specificity = 1e-10
		if self.determinism < 0: self.determinism = 0.0


	def get_generation_ps(self, stimuli, category):

		# compute contrast sum similarity
		contrast_examples   = self.exemplars[self.assignments != category]
		contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = self.between)

		# compute target sum similarity
		target_examples = self.exemplars[self.assignments == category]
		target_ss   = self._sum_similarity(stimuli, target_examples, param = self.within)

		# aggregate target and contrast similarity
		aggregate = contrast_ss + target_ss

		# nan out members of the target category
		known_members = Funcs.intersect2d(stimuli, target_examples)
		aggregate[known_members] = np.nan

		ps = Funcs.softmax(aggregate, theta = self.determinism)
		return ps

