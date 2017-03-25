import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Exemplar

class CopyTweak(Exemplar):
	"""
		Continuous implementation of the copy-and-tweak model.
	"""

	model = 'Copy and Tweak'
	parameter_names = ['specificity', 'determinism']
	parameter_rules = dict(
			specificity = dict(min = 1e-10),
			determinism = dict(min = 0),
		)

	@staticmethod
	def _make_rvs(fmt = dict):
		""" Return random parameters """
		return [np.random.uniform(0.1, 6.0), # specificity
						np.random.uniform(0.1, 6.0)] # determinism

	def get_generation_ps(self, stimuli, category):

		# return uniform probabilities if there are no exemplars
		target_is_populated = any(self.assignments == category)
		if not target_is_populated:
			ncandidates = stimuli.shape[0]
			return np.ones(ncandidates) / float(ncandidates)

		# get pairwise similarities
		similarity = self._sum_similarity(stimuli, self.categories[category])

		# NaN out known members
		known_members = Funcs.intersect2d(stimuli, self.categories[category])
		similarity[known_members] = np.nan

		# get generation probabilities given each source
		ps = Funcs.softmax(similarity, theta = self.determinism)
		return ps


