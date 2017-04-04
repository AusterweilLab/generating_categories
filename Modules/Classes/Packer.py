import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Exemplar


class Packer(Exemplar):
	"""
	The three-parameter PACKER Model
	"""

	model = 'PACKER'
	parameter_names = ['specificity', 'tradeoff', 'determinism'] 
	parameter_rules = dict(
			specificity = dict(min = 1e-10),
			tradeoff = dict(min = 0.0, max = 1.0),
			determinism = dict(min = 0.0),
		)

	@staticmethod
	def _make_rvs():
		""" Return random parameters """
		return [
			np.random.uniform(0.1, 6.0),  # specificity
			np.random.uniform(0.0, 1.0),	# tradeoff
			np.random.uniform(0.1, 6.0)		# determinism
		] 


	def get_generation_ps(self, stimuli, category):

		# compute contrast sum similarity
		contrast_examples   = self.exemplars[self.assignments != category]
		contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 + self.tradeoff)

		# compute target sum similarity
		target_examples = self.exemplars[self.assignments == category]
		target_ss   = self._sum_similarity(stimuli, target_examples, param = self.tradeoff)

		# aggregate target and contrast similarity
		aggregate = contrast_ss + target_ss

		# nan out members of the target category
		known_members = Funcs.intersect2d(stimuli, target_examples)
		aggregate[known_members] = np.nan

		ps = Funcs.softmax(aggregate, theta = self.determinism)
		return ps



class CopyTweak(Exemplar):
	"""
		Continuous implementation of the copy-and-tweak model.
	"""

	model = 'Copy and Tweak'
	parameter_names = ['specificity', 'determinism']
	parameter_rules = dict(
			specificity = dict(min = 1e-10),
			determinism = dict(min = 0.0),
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

