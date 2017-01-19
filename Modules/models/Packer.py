import numpy as np

# imports from module
import utils
from Model import Model

class Packer(Model):
	"""
	Exemplar similarity implementation of the packing model.
	"""

	model = 'PACKER'
	parameter_names = [
		'specificity', # > 0 
		'between',  # > 0
		'within', # > 0
		'determinism' # > 0
	] # OPTIONAL: wts

	def _param_handler_(self):
		super(Packer, self)._param_handler_()
		if self.specificity <= 0: self.specificity = 1e-10
		if self.between <= 0: self.between = 1e-10
		if self.within <= 0: self.within = 1e-10
		if self.determinism <= 0: self.determinism = 1e-10


	def _get_ss(self, candidates, class_items, contribution_param):
		""" function to compute summed similarity """
		distance   = utils.pdist(candidates, class_items, w = self.wts)
		similarity = np.exp(-float(self.specificity) * distance)
		similarity = similarity * float(contribution_param)
		return np.sum(similarity, axis = 1)


	def get_generation_ps(self, stimuli, category):

		# compute contrast sum similarity
		contrast_examples   = self.exemplars[self.assignments != category]
		contrast_ss   = self._get_ss(stimuli, contrast_examples, -1.0 * self.between)

		# compute target sum similarity
		target_examples = self.exemplars[self.assignments == category]
		target_ss   = self._get_ss(stimuli, target_examples, self.within)

		# aggregate target and contrast similarity
		total = contrast_ss + target_ss
		total = np.exp(float(self.determinism) * total)

		# zero out members of the target category
		if any(self.assignments == category):
			known_members = utils.intersect2d(stimuli, target_examples)
			total[known_members] = 0.0

		ps = total / float(sum(total))
		return ps