import numpy as np

# imports from module
import utils
from Model import Model

class CopyTweak(Model):
	"""
		Exemplar similarity implementation of the copy-and-tweak model.
	"""

	model = 'Copy & Tweak'
	parameter_names = [
		'specificity', # > 0
		'within_pref', # any value
		'tolerance', # 0 < tolerance <= 1
		'determinism' # > 0
	]

	def _param_handler_(self):
		super(CopyTweak, self)._param_handler_()
		if self.specificity <= 0: self.specificity = 1e-10
		if self.tolerance <= 0: self.tolerance = 1e-10
		if self.tolerance > 1.0: self.tolerance = 1.0
		if self.determinism <= 0: self.determinism = 1e-10

	def get_generation_ps(self, stimuli, category):

		# get source probabilities
		source_ps = np.ones(self.exemplars.shape[0])	* -float(self.within_pref)
		source_ps[self.assignments == category] = float(self.within_pref)
		source_ps = np.exp(source_ps)
		source_ps = source_ps / float(sum(source_ps))

		# get pairwise similarities
		distances  = utils.pdist(stimuli, self.exemplars, w = self.wts)
		similarity = np.exp(-1.0 * self.specificity * distances)

		# get generation probabilities given each source
		generation_ps = np.exp(float(self.determinism) * similarity)

		# zero out probabilities above the similiarity tolerance
		generation_ps[similarity > self.tolerance] = 0.0

		# zero out examples already in the target category
		if any(self.assignments == category):
			known_members = utils.intersect2d(stimuli, self.categories[category])
			generation_ps[known_members] = 0.0

		# normalize
		generation_ps = generation_ps / generation_ps.sum(axis = 0, keepdims = True)
		
		# find nan columns to prevent nan ps
		nancols = np.all(np.isnan(generation_ps), axis = 0)
		generation_ps[:,nancols] = 1.0 / stimuli.shape[0]

		# multiply generation and source probabilities, then sum over sources
		ps = generation_ps * source_ps[None, :]
	
		ps = np.sum(ps, axis = 1)
		return ps


