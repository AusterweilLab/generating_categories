import numpy as np
from scipy.stats import multivariate_normal

# imports from module
import Modules.Funcs as Funcs
from Model import Model

class ConjugateJK13(Model):
	"""
	A conjugate version of the Jern & Kemp (2013) heirarchical sampling
	Model. Categories are represented as multivariate normal, and the 
	domain covariance is inverse-wishart.
	"""

	model = "Hierarchical Sampling"
	parameter_names = [
		'category_mean_bias', # > 0
		'category_variance_bias', # > p - 1
		'domain_variance_bias', # > 0
		'determinism' # > 0 
		]

	@staticmethod
	def rvs(nf = 2):
		params = [
			np.random.uniform(0.01, 3.0), # category_mean_bias
			np.random.uniform(nf-0.99, nf+2.0), # category_variance_bias
			np.random.uniform(0.01, 5.0), # domain_variance_bias
			np.random.uniform(0.1, 6.0) # determinism
		]
		return params

	def _update_(self):
		"""
		This model additionally requires setting of the domain 
		parameters and priors	on update.
		"""

		# standard update procedure
		super(ConjugateJK13, self)._update_()

		# set prior mean.
		self.category_prior_mean = np.zeros(self.nfeatures)

		# infer domain Sigma
		self.Domain = np.array(self.prior_variance, copy=True)
		for y in range(self.ncategories):
			if self.nexemplars[y] < 2: continue
			C = np.cov(self.categories[y], rowvar = False)
			self.Domain += C


	def _param_handler_(self):
		super(ConjugateJK13, self)._param_handler_()
		if self.category_mean_bias <= 0: self.category_mean_bias = 1e-10
		if self.category_variance_bias <= self.nfeatures - 1.0: 
			self.category_variance_bias = self.nfeatures + 1e-10
		if self.domain_variance_bias <= 0: self.domain_variance_bias = 1e-10
		if self.determinism <= 0: self.determinism = 1e-10


	def _wts_handler_(self):
		"""
			Converts wts into a covaraince matrix.
			Weights are implemented as differences in the assumed [prior]
			Domain covariance.
		"""
		super(ConjugateJK13, self)._wts_handler_()
		self.prior_variance = np.eye(self.nfeatures) * self.nfeatures
		inds = np.diag_indices(self.nfeatures)
		self.prior_variance[inds] *= self.wts

	def get_generation_ps(self, stimuli, category):
		target_is_populated = any(self.assignments == category)

		# get target category stats
		if target_is_populated:
			xbar = np.mean(self.categories[category], axis = 0)
			n = self.nexemplars[category]
			if n < 2:
				C = np.zeros((self.nfeatures, self.nfeatures))
			else:
				C = np.cov(self.categories[category], rowvar = False)

		# infer target category mu
		if not target_is_populated:
			mu = self.category_prior_mean
		else:
			mu =  self.category_mean_bias * self.category_prior_mean
			mu += n * xbar
			mu /= self.category_mean_bias + n

		# compute target category Sigma
		if not target_is_populated:
			Sigma = self.Domain
		else:
			ratio = (self.category_mean_bias * n) / (self.category_mean_bias + n)
			Sigma = ratio * np.outer(xbar - mu, xbar - mu)
			Sigma += self.Domain * self.category_variance_bias + C
			Sigma /= self.category_variance_bias + n

		# get relative densities
		target_dist = multivariate_normal(mean = mu, cov = Sigma)
		density = target_dist.pdf(stimuli)
		density = np.exp(self.determinism * density)

		# zero out examples already in the target category
		if target_is_populated:
			known_members = Funcs.intersect2d(stimuli, self.categories[category])
			density[known_members] = 0.0

		# convert to probability distribution
		ps = density / float(sum(density))
		return ps



		


