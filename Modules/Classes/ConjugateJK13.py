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
	num_features    = 2 # hard coded number of assumed features
	parameter_names = [	'category_mean_bias',   'category_variance_bias',
											'domain_variance_bias', 'determinism' ]
	parameter_rules = dict(
			category_mean_bias = dict(min = 1e-10),
			category_variance_bias = dict(min = num_features - 1 + 1e-10),
			domain_variance_bias = dict(min = 1e-03),
			determinism = dict(min = 0),
		)


	@staticmethod
	def _make_rvs():
		""" Return random parameters """
		nf = ConjugateJK13.num_features
		return [
			np.random.uniform(0.01, 0.5), # category_mean_bias, biased small
			np.random.uniform(nf-0.99, nf+2.0), # category_variance_bias
			np.random.uniform(0.01, 5.0), # domain_variance_bias
			np.random.uniform(0.1, 6.0) # determinism
		]
	

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
		self.prior_variance *= self.domain_variance_bias

	def get_generation_ps(self, stimuli, category,task='generate'):

		# random response if there are no target members.
		target_is_populated = any(self.assignments == category)
		if not target_is_populated:
			ncandidates = stimuli.shape[0]
			return np.ones(ncandidates) / float(ncandidates)

		# get target category stats
		xbar = np.mean(self.categories[category], axis = 0)
		n = self.nexemplars[category]
		if n < 2:
			C = np.zeros((self.nfeatures, self.nfeatures))
		else:
			C = np.cov(self.categories[category], rowvar = False)

		# compute mu for target category
		mu =  self.category_mean_bias * self.category_prior_mean
		mu += n * xbar
		mu /= self.category_mean_bias + n

		# compute target category Sigma
		ratio = (self.category_mean_bias * n) / (self.category_mean_bias + n)
		Sigma = ratio * np.outer(xbar - mu, xbar - mu)
		Sigma += self.Domain * self.category_variance_bias + C
		Sigma /= self.category_variance_bias + n

		# get relative densities
                if np.isnan(Sigma).any() or np.isinf(Sigma).any():
                        #target_dist = np.ones(mu.shape) * np.nan
                        density = np.ones(len(stimuli)) * np.nan
                else:
                        # #170418 Implementing representational draws
                        # # See equation 7 in Tenenbaum & Griffiths 2001 cogsci proceedings paper
                        # S = categories[category]
                        # mmu = m-mu
                        # Vinv = np.linalg.inv(V)
                        # rep = N * log(S) - N * np.dot(np.dot(mmu.transpose(),Vinv),mmu) - trace(np.dot(S,Vinv))
                        
                        target_dist = multivariate_normal(mean = mu, cov = Sigma)
                        density = target_dist.pdf(stimuli)
                        
                if task is 'generate': 
		        # NaN out known members - only for task=generate
		        known_members = Funcs.intersect2d(stimuli, self.categories[category])
		        density[known_members] = np.nan
		        ps = Funcs.softmax(density, theta = self.determinism)
                elif task is 'assign' or task is 'error':
                        ## Do the same for the contrast categor
                        # get target category stats
		        xbar_flip = np.mean(self.categories[1-category], axis = 0)
		        n_flip = self.nexemplars[1-category]
		        if n_flip < 2:
			        C_flip = np.zeros((self.nfeatures, self.nfeatures))
		        else:
			        C_flip = np.cov(self.categories[1-category], rowvar = False)
                                
		        # compute mu for target category
		        mu_flip =  self.category_mean_bias * self.category_prior_mean
		        mu_flip += n_flip * xbar_flip
		        mu_flip /= self.category_mean_bias + n_flip
                        
		        # compute target category Sigma
		        ratio_flip = (self.category_mean_bias * n_flip) / (self.category_mean_bias + n_flip)
		        Sigma_flip = ratio_flip * np.outer(xbar_flip - mu_flip, xbar_flip - mu_flip)
		        Sigma_flip += self.Domain * self.category_variance_bias + C_flip
		        Sigma_flip /= self.category_variance_bias + n_flip
                        
		        # get relative densities
                        if np.isnan(Sigma_flip).any() or np.isinf(Sigma_flip).any():
                                #target_dist_flip = np.ones(mu_flip.shape) * np.nan
                                density_flip = np.ones(len(stimuli)) * np.nan
                        else:
		                target_dist_flip = multivariate_normal(mean = mu_flip, cov = Sigma_flip)                                
		                density_flip = target_dist_flip.pdf(stimuli)


                        ps = []
                        for i in range(len(density)):
                                density_element = np.array([density[i],
                                                            density_flip[i]])
                                ps_element = Funcs.softmax(density_element, theta = self.determinism)
                                ps = np.append(ps,ps_element[0])                        

		return ps



		


