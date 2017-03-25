import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Exemplar

class Packer(Exemplar):
	"""
	Exemplar similarity implementation of the packing model.
	"""

	model = 'PACKER'
	parameter_names = ['specificity', 'between', 'within', 'determinism'] 
	parameter_rules = dict(
			specificity = dict(min = 1e-10),
			determinism = dict(min = 0),
		)

	@staticmethod
	def _make_rvs():
		""" Return random parameters """
		return [
				np.random.uniform(0.1, 6.0), # specificity
				np.random.uniform(-6.0, 0.0), # between. biased negative.
				np.random.uniform(0.0, 6.0), # within. biased positive
				np.random.uniform(0.1, 6.0) # determinism
			]

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

