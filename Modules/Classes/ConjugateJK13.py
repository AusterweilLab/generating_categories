import numpy as np
import random
from scipy.stats import multivariate_normal
from scipy.stats import invwishart

# imports from module
import Modules.Funcs as Funcs
from Model import HierSamp

class ConjugateJK13(HierSamp):
    """
    A conjugate version of the Jern & Kemp (2013) heirarchical sampling
    Model. Categories are represented as multivariate normal, and the 
    domain covariance is inverse-wishart.
    """

    model = "Hierarchical Sampling"
    modelshort = "Hier. Samp."
    modelprint = "Hier. Bayes"
    num_features = 2 #hard code on first init, then update whenever trials come in
    parameter_names = [    'category_mean_bias',   'category_variance_bias',
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
        parameters and priors    on update.
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

        #update number of features
        self.num_features = self.nfeatures

    def _wts_handler_(self):
        """
            Converts wts into a covariance matrix.
            Weights are implemented as differences in the assumed [prior]
            Domain covariance.
        """
        super(ConjugateJK13, self)._wts_handler_()
        self.prior_variance = np.eye(self.nfeatures) * self.nfeatures
        inds = np.diag_indices(self.nfeatures)
        self.prior_variance[inds] *= self.wts
        self.prior_variance *= self.domain_variance_bias

    def get_musig(self, stimuli, category):
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

        return (mu,Sigma)

    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False,wrap_ax = None):
        # random response if there are no target members.
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        mu,Sigma = self.get_musig(stimuli, category)
                
        # get relative densities
        if np.isnan(Sigma).any() or np.isinf(Sigma).any():
            #target_dist = np.ones(mu.shape) * np.nan
            density = np.ones(len(stimuli)) * np.nan
        else:
            target_dist = multivariate_normal(mean = mu, cov = Sigma)
            if not wrap_ax is None:
                density = self._wrapped_density(target_dist,stimuli,wrap_ax)
            else:
                density = target_dist.pdf(stimuli)
                
        if task is 'generate': 
            # NaN out known members - only for task=generate            
            known_members = Funcs.intersect2d(stimuli, self.categories[category])
            density[known_members] = np.nan
            ps = Funcs.softmax(density, theta = self.determinism)
        elif task is 'assign' or task is 'error':
            # get relative densities
            mu_flip, Sigma_flip = self.get_musig(stimuli,1-category)
            if np.isnan(Sigma_flip).any() or np.isinf(Sigma_flip).any():
                #target_dist_flip = np.ones(mu_flip.shape) * np.nan
                density_flip = np.ones(len(stimuli)) * np.nan
            else:
                target_dist_flip = multivariate_normal(mean = mu_flip, cov = Sigma_flip)
                if not wrap_ax is None:
                    density_flip = self._wrapped_density(target_dist_flip,stimuli,wrap_ax)
                else:
                    density_flip = target_dist_flip.pdf(stimuli)

            ps = []
            for i in range(len(density)):
                density_element = np.array([density[i],
                                            density_flip[i]])
                ps_element = Funcs.softmax(density_element, theta = self.determinism)
                ps = np.append(ps,ps_element[0])                        
        return ps



        


class RepresentJK13(HierSamp):
    """
    A conjugate version of the Jern & Kemp (2013) heirarchical sampling
    Model with representativeness. Categories are represented as a ratio of  multivariate normals,
        and the domain covariance is inverse-wishart.
    """

    model = "Hierarchical Sampling With Representativeness"
    modelshort = "Representative"
    modelprint = "Representativeness"
    num_features    = 2 # hard coded number of assumed features
    #num_features = self.nfeatures
    parameter_names = [    'category_mean_bias',   'category_variance_bias',
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
        nf = RepresentJK13.num_features
        return [
            np.random.uniform(0.01, 0.5), # category_mean_bias, biased small
            np.random.uniform(nf-0.99, nf+5.0), # category_variance_bias
            np.random.uniform(0.01, 5.0), # domain_variance_bias
            np.random.uniform(0.1, 6.0) # determinism
        ]
    

    def _update_(self):
        """
        This model additionally requires setting of the domain 
        parameters and priors    on update.
        """
        # standard update procedure
        super(RepresentJK13, self)._update_()

        # infer domain Sigma
        self.Domain = np.array(self.prior_variance, copy=True)
        for y in range(self.ncategories):            
            #if self.nexemplars[y] < 2: continue
            #C = np.cov(self.categories[y], rowvar = False)
            (xbar,C) = self.catStats(y)
            self.Domain += C

        # set prior mean.
        #If an axis is wrapped, however, set the prior mean to be center of the first populated category
        if self.wrap_ax is None:
            self.category_prior_mean = np.zeros(self.nfeatures) 
        else:
            self.category_prior_mean = xbar
        #Update num features for correct parm rules
        self.num_features = self.nfeatures

    def _wts_handler_(self):
        """
            Converts wts into a covaraince matrix.
            Weights are implemented as differences in the assumed [prior]
            Domain covariance.
        """
        super(RepresentJK13, self)._wts_handler_()
        self.prior_variance = np.eye(self.nfeatures) * self.nfeatures
        inds = np.diag_indices(self.nfeatures)
        self.prior_variance[inds] *= self.wts
        self.prior_variance *= self.domain_variance_bias


    def catStats(self,category):
        # Get empirical mean and cov
        wrap_ax = self.wrap_ax
        n = self.nexemplars[category]
        if not wrap_ax is None:
            wrap_ax = int(wrap_ax)
            ax_range = self.stimrange[0]['max'] - self.stimrange[0]['min']
            ax_step = self.stimstep[0]
            cat = self.categories[category].copy()
            stim_range = np.max(cat[:,wrap_ax]) - np.min(cat[:,wrap_ax])
            if stim_range>(ax_range/2):                    
                #Stimuli outside half the range get adjusted up to the first wrap
                new_exm = cat[cat[:,wrap_ax]>=0,:]
                shift_exm = cat[cat[:,wrap_ax]<0,:]
                #Adj the wrap_axis of shifted exm
                shift_exm[:,wrap_ax] = shift_exm[:,wrap_ax] + ax_range + ax_step
                new_exm = np.concatenate([new_exm,shift_exm],axis=0)
                xbar = np.mean(new_exm,axis=0)
                #Place mean in the current range of stimuli
                xbar[wrap_ax] = xbar[wrap_ax] - ax_range - ax_step
            else:
                new_exm = cat
                xbar = np.mean(cat, axis=0)
        else:                                                        
            xbar = np.mean(self.categories[category], axis = 0)
            new_exm = self.categories[category]
            
        #Now deal with sigma
        if n < 2:
            C = np.zeros((self.nfeatures, self.nfeatures))
        else:
            C = np.cov(new_exm, rowvar = False)                

        return (xbar,C)
    
    def get_musig(self, stimuli, category,wrap_ax=None):
        self.stimuli = stimuli
        self.wrap_ax = wrap_ax
        # random response if there are no target members.
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            mu = []
            #randomly sample mu from uniform                        
            # for nf in range(self.nfeatures):
            #     mu += [np.random.uniform(self.stimrange[nf]['min'],
            #                              self.stimrange[nf]['max'])]
            # mu = np.array(mu)
            #mu = self.category_mean_bias * self.category_prior_mean #isn't this more correct?
            mu = self.category_prior_mean #isn't this more correct?
            # Need to think about how to handle the influence of the prior mean... -- implications on whether it's appropriate for ConjugateJK13 to be a uniform random sample without any members

            Sigma = self.Domain * self.category_variance_bias
        else:
            n = self.nexemplars[category]
            (xbar,C) = self.catStats(category)            
            # compute mu for target category
            mu =  self.category_mean_bias * self.category_prior_mean
            mu += n * xbar
            mu /= self.category_mean_bias + n

            # compute target category Sigma
            ratio = (self.category_mean_bias * n) / (self.category_mean_bias + n)
            Sigma = ratio * np.outer(xbar - mu, xbar - mu)
            Sigma += self.Domain * self.category_variance_bias + C
            Sigma /= self.category_variance_bias + n
        return (mu,Sigma)

    def get_generation_ps(self, stimuli, category, task='generate', seedrng = False, wrap_ax = None):
        if seedrng:
            np.random.seed(234983) #some arbitrary seed value here

        target_is_populated = any(self.assignments == category)                
        mu,Sigma = self.get_musig(stimuli, category,wrap_ax)
                
        # get relative densities
        if np.isnan(Sigma).any() or np.isinf(Sigma).any():
            #target_dist = np.ones(mu.shape) * np.nan
            density = np.ones(len(stimuli)) * np.nan
        else:
            # #270418 Implementing representational draws
            target_dist_target = multivariate_normal(mean = mu, cov = Sigma)
            if not wrap_ax is None:
                likelihood_target = self._wrapped_density(target_dist_target,stimuli,wrap_ax)
            else:
                likelihood_target = target_dist_target.pdf(stimuli)

            likelihood_alt = []
            prior_dens = []
            #Get parameters for all alt categories (alternative hypothesis)
            for c_alt in range(self.ncategories):
                if not c_alt == category: #Continue (pass) if c_alt is target category                    
                    mu_alt, Sigma_alt = self.get_musig(stimuli, c_alt,wrap_ax)
                    target_dist_alt = multivariate_normal(mean = mu_alt, cov = Sigma_alt)
                    if not wrap_ax is None:
                        likelihood_alt += [self._wrapped_density(target_dist_alt,stimuli,wrap_ax)]
                    else:
                        likelihood_alt += [target_dist_alt.pdf(stimuli)]

                    if self.ncategories > 2:
                        #Specify priors
                        prior_dist_n = multivariate_normal(mean=self.category_prior_mean,cov = Sigma_alt/self.category_mean_bias) #got the sigma_alt/cat_mean_bias from wikipedia
                        #Use custom invwishart pdf because scipy's doesn't like p-1<df<p
                        invw_pdf = Funcs.invwishartpdf(Sigma_alt,scale=self.Domain,nu=self.category_variance_bias)
                        prior_dens += [prior_dist_n.pdf(mu_alt) * invw_pdf]#[prior_dist_n.pdf(mu_alt) * prior_dist_iw.pdf(Sigma_alt)]

            if self.ncategories > 2:
                prior = Funcs.softmax(np.array(prior_dens), theta=1,toggle=False)
            else:
                prior = [1]
                
            denom = 0
            for ci in range(len(prior)):
                if len(likelihood_alt)>0:
                    denom += likelihood_alt[ci] * prior[ci]
                else:
                    #If for whatever reason there is no alternative category
                    denom = 1
            
            density = np.log(likelihood_target/denom)
        if task is 'generate': 
            # NaN out known members - only for task=generate
            if target_is_populated:
                known_members = Funcs.intersect2d(stimuli, self.categories[category])
                density[known_members] = np.nan                                
            ps = Funcs.softmax(density, theta = self.determinism)                
        elif task is 'assign' or task is 'error':
            # get relative densities
            if np.isnan(Sigma).any() or np.isinf(Sigma).any():
                density_flip = np.ones(len(stimuli)) * np.nan
            else:
                density_flip = np.log(likelihood_alt/likelihood_target)
            ps = []
            for i in range(len(density)):
                density_element = np.array([density[i],
                                            density_flip[i]])
                ps_element = Funcs.softmax(density_element, theta = self.determinism)
                ps = np.append(ps,ps_element[0])
        #return (ps,likelihood_alt,likelihood_target,Sigma,Sigma_alt)
        return ps





class NegatedSpace(HierSamp):
    """
    'Dumb' implementation of a negated-space model
    """

    model = "Negated Space"
    modelshort = "Neg. Sp."
    modelprint = "Neg. Sp."
    num_features = 2 #hard code on first init, then update whenever trials come in
    parameter_names = ['determinism' ]
    parameter_rules = dict(
            determinism = dict(min = 0),
        )


    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        nf = NegatedSpace.num_features
        return [
            np.random.uniform(0.1, 6.0) # determinism
        ]
    

    def _update_(self):
        """
        This model additionally requires setting of the domain 
        parameters and priors    on update.
        """

        # standard update procedure
        super(NegatedSpace, self)._update_()

        # # Get observed learned category covariance
        # C = []
        # for y in range(self.ncategories):
        #     if self.nexemplars[y] < 2:
        #         # If less than 2 trained exemplars, no covariance matrix
        #         C += None
        #     C += np.cov(self.categories[y],rowvar=False)

        # # set prior mean.
        # self.category_prior_mean = np.zeros(self.nfeatures)

        # # infer domain Sigma
        # self.Domain = np.array(self.prior_variance, copy=True)
        # for y in range(self.ncategories):
        #     if self.nexemplars[y] < 2: continue
        #     C = np.cov(self.categories[y], rowvar = False)
        #     self.Domain += C

        #update number of features
        self.num_features = self.nfeatures

    # def _wts_handler_(self):
    #     """
    #         Converts wts into a covaraince matrix.
    #         Weights are implemented as differences in the assumed [prior]
    #         Domain covariance.
    #     """
    #     super(ConjugateJK13, self)._wts_handler_()
    #     self.prior_variance = np.eye(self.nfeatures) * self.nfeatures
    #     inds = np.diag_indices(self.nfeatures)
    #     self.prior_variance[inds] *= self.wts
    #     self.prior_variance *= self.domain_variance_bias

    def get_musig(self, stimuli, category):
        # get target category stats
        mu = np.mean(self.categories[category], axis = 0)
        n = self.nexemplars[category]
        if n < 2:
            Sigma = np.zeros((self.nfeatures, self.nfeatures))
        else:
            Sigma = np.cov(self.categories[category], rowvar = False)

        # compute mu for target category
        # mu =  self.category_mean_bias * self.category_prior_mean
        # mu += n * xbar
        # mu /= self.category_mean_bias + n

        # compute target category Sigma
        # ratio = (self.category_mean_bias * n) / (self.category_mean_bias + n)
        # Sigma = ratio * np.outer(xbar - mu, xbar - mu)
        # Sigma += self.Domain * self.category_variance_bias + C
        # Sigma /= self.category_variance_bias + n

        return (mu,Sigma)

    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False,wrap_ax = None):
        # random response if there are no target members.
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)
        mus = []
        Sigmas = []
        for ci in range(self.ncategories):
            mu,Sigma = self.get_musig(stimuli, ci)
            # get relative densities
            if np.isnan(Sigma).any() or np.isinf(Sigma).any():
                #target_dist = np.ones(mu.shape) * np.nan
                density = np.ones(len(stimuli)) * np.nan
            else:
                target_dist = multivariate_normal(mean = mu, cov = Sigma)
                if not wrap_ax is None:
                    density = self._wrapped_density(target_dist,stimuli,wrap_ax)
                else:
                    density = target_dist.pdf(stimuli)
                    #Continue implementing dumb model...Xian 150719
            mus += mu
            Sigmas += Sigma
                

                
        if task is 'generate': 
            # NaN out known members - only for task=generate            
            known_members = Funcs.intersect2d(stimuli, self.categories[category])
            density[known_members] = np.nan
            ps = Funcs.softmax(density, theta = self.determinism)
        elif task is 'assign' or task is 'error':
            # get relative densities
            mu_flip, Sigma_flip = self.get_musig(stimuli,1-category)
            if np.isnan(Sigma_flip).any() or np.isinf(Sigma_flip).any():
                #target_dist_flip = np.ones(mu_flip.shape) * np.nan
                density_flip = np.ones(len(stimuli)) * np.nan
            else:
                target_dist_flip = multivariate_normal(mean = mu_flip, cov = Sigma_flip)
                if not wrap_ax is None:
                    density_flip = self._wrapped_density(target_dist_flip,stimuli,wrap_ax)
                else:
                    density_flip = target_dist_flip.pdf(stimuli)

            ps = []
            for i in range(len(density)):
                density_element = np.array([density[i],
                                            density_flip[i]])
                ps_element = Funcs.softmax(density_element, theta = self.determinism)
                ps = np.append(ps,ps_element[0])                        
        return ps

