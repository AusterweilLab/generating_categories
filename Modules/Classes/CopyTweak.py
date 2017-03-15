import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Exemplar

class CopyTweak(Exemplar):
	"""
		Continuous implementation of the copy-and-tweak model.
	"""

	model = 'Copy and Tweak'
	parameter_names = [
		'specificity', # > 0
		'determinism' # > 0
	]


	@staticmethod
	def rvs(fmt = dict):
		"""
		Return random parameters in dict or list format.
		"""
		params = [np.random.uniform(0.1, 6.0), # specificity
							np.random.uniform(0.1, 6.0)] # determinism

		if fmt not in [dict, list]:
			raise Exception('Format must be dict or list.')

		if fmt == list:
			return params
		else:
			return dict(zip(CopyTweak.parameter_names, params))


	def _param_handler_(self):
		super(CopyTweak, self)._param_handler_()
		if self.specificity <= 0: self.specificity = 1e-10
		if self.determinism < 0: self.determinism = 0.0


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


