import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Model

class PPOLR(Model):
	"""
	Exemplar similarity implementation of the packing model.
	"""

	model = 'PPOLR'
	parameter_names = [
		'specificity', # c > 0 
		'between',  # phi, any real
		'within', # gamma, any real
		'retrieval_determinism', # theta_source > 0
		'weights_determinism', # theta_wts > 0
		'determinism', # theta_generate > 0
	] 

	@staticmethod
	def rvs():
		params = [
			np.random.uniform(0.1, 6.0), # specificity
			np.random.uniform(-6.0, 0.0), # between. biased negative.
			np.random.uniform(0.0, 6.0), # within. biased positive
			np.random.uniform(0.1, 6.0), # retrieval determinism
			np.random.uniform(0.1, 6.0), # weights determinism
			np.random.uniform(0.1, 6.0) # generation determinism
		]
		return params

	def _param_handler_(self):
		super(PPOLR, self)._param_handler_()
		if self.specificity <= 0:   self.specificity = 1e-10
		if self.retrieval_determinism < 0: self.retrieval_determinism = 0
		if self.weights_determinism < 0: self.weights_determinism = 0
		if self.determinism < 0:  self.determinism = 0


	def _update_(self):
		"""
		This model additionally requires setting the:
			- category-specific wts
			- exemplar retrieval probabilities
		"""

		# standard update procedure
		super(PPOLR, self)._update_()

		self.exemplar_ps = np.empty(sum(self.nexemplars))
		self.class_wts = np.empty((self.ncategories, self.nfeatures))
		for c, members in enumerate(self.categories):

			# class weights
			ranges = np.ptp(members, axis = 0)
			self.class_wts[c,:] = Funcs.softmax(ranges, theta = -self.weights_determinism)

			# exemplar probabilities
			ss = self._get_ss(members, members)
			ps = Funcs.softmax(ss, theta = self.retrieval_determinism)			
			self.exemplar_ps[self.assignments==c]  = ps / self.ncategories


	def _get_ss(self, X, Y, param = 1.0,	wts  = None):
		""" 
		function to compute summed similarity along rows of 
		X across all items in Y. Resulting array will have one element 
		per row of X.
		"""

		if wts is None: wts = self.wts
		distance   = Funcs.pdist(np.atleast_2d(X), np.atleast_2d(Y), w = self.wts)
		similarity = np.exp(-float(self.specificity) * distance)
		similarity = similarity * float(param)
		return np.sum(similarity, axis = 1)


	def get_generation_ps(self, stimuli, category):
		
		# find out if any candidates are known members of the target
		if any(self.assignments == category):
			known_members = Funcs.intersect2d(stimuli, self.categories[category])

		# get generation ps, given each source
		generate_ps = np.empty((stimuli.shape[0], sum(self.nexemplars)))
		for c, members in enumerate(self.categories):

			# set category params
			if c == category: param = self.within
			else: param = self.between
			wts = self.class_wts[c,:]

			# compute pairwise similarities
			distance = Funcs.pdist(stimuli, members, w = wts)
			similarity = np.exp(-float(self.specificity) * distance)
			similarity *= param

			# convert known members to -inf (0 after exp)
			if any(self.assignments == category):
				similarity[known_members,:] = np.nan

			# softmax for ps
			idx = self.assignments == c
			generate_ps[:,idx] = Funcs.softmax(similarity, theta = self.determinism)

		ps = np.sum(generate_ps * self.exemplar_ps[None,:], axis = 1)
		return ps


