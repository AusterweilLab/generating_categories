import numpy as np
from scipy.stats import multivariate_normal

# imports from module
import Modules.Funcs as Funcs
from Modules.Classes.Model import Exemplar


class Packer(Exemplar):
    """
    The three-parameter PACKER Model
    """

    model = 'PACKER'
    modelshort = 'PACKER'
    modelprint = 'PACKER'
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):

        # if not wrap_ax is None:
        #     ax_ranges = np.ptp(stimuli,axis=0)
        #     if not ax_ranges[0]==ax_ranges[1]:
        #         raise ValueError('Range of x-axis ({}) does not match range of y-axis({})'.format(ax_ranges[0],ax_ranges[1]))
        #     else:
        #         ax_range = ax_ranges[0]
        #     ax_step = abs(stimuli[1,0]-stimuli[0,0]) #assume consistent steps -- dangerous if not the case though
        # compute contrast sum similarity
        #New attempt 110418. Updated 170418 - theta_cntrst is for contrast, theta_target is tradeoff for target
        contrast_examples   = self.exemplars[self.assignments != category]
        contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst)
        # compute target sum similarity
        target_examples = self.exemplars[self.assignments == category]
        target_ss   = self._sum_similarity(stimuli, target_examples, param = self.theta_target)
        #End new attempt 110418
        
        # aggregate target and contrast similarity
        aggregate = contrast_ss + target_ss
        # add baseline similarity
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, target_examples)
            aggregate[known_members] = np.nan
            ps = Funcs.softmax(aggregate, theta = 1.0)                       
            #ps = Funcs.softmax(aggregate, theta = self.determinism)                        
        elif task == 'assign' or task == 'error':
            #New test 110418
            #compute contrast and target ss if stimuli is assigned
            #to other cateogry
            contrast_examples_flip = target_examples
            contrast_ss_flip = self._sum_similarity(stimuli,
                                                    contrast_examples_flip,
                                                    param = -1.0 * self.theta_cntrst)
            target_examples_flip = contrast_examples
            target_ss_flip   = self._sum_similarity(stimuli,
                                                    target_examples_flip,
                                                    param = self.theta_target)
            #End test 110418

            aggregate_flip = target_ss_flip + contrast_ss_flip

            #Go through each stimulus and calculate their ps
            ps = np.array([])
            for i in range(len(aggregate)):
                    agg_element = np.array([aggregate[i],aggregate_flip[i]])
                    #ps_element = Funcs.softmax(agg_element, theta = self.determinism)
                    ps_element = Funcs.softmax(agg_element, theta = 1.0)
                    ps = np.append(ps,ps_element[0])
                    
        return ps

        
class PackerEuc(Exemplar):
    """
    The three-parameter PACKER Model with Euclidean distance
    """

    model = 'PACKEREuc'
    modelshort = 'PACKEREuc'
    modelprint = 'PACKEREuc'
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):

        # compute contrast sum similarity
        #New attempt 110418. Updated 170418 - theta_cntrst is for contrast, theta_target is tradeoff for target
        contrast_examples   = self.exemplars[self.assignments != category]
        contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst,p=2)
        # compute target sum similarity
        target_examples = self.exemplars[self.assignments == category]
        target_ss   = self._sum_similarity(stimuli, target_examples, param = self.theta_target,p=2)
        #End new attempt 110418
                
        aggregate = contrast_ss + target_ss
        # add baseline similarity
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, target_examples)
            aggregate[known_members] = np.nan
            ps = Funcs.softmax(aggregate, theta = 1.0)                       
            #ps = Funcs.softmax(aggregate, theta = self.determinism)                        
        elif task == 'assign' or task == 'error':
            #New test 110418
            #compute contrast and target ss if stimuli is assigned
            #to other cateogry
            contrast_examples_flip = target_examples
            contrast_ss_flip = self._sum_similarity(stimuli,
                                                    contrast_examples_flip,
                                                    param = -1.0 * self.theta_cntrst,
                                                    p=2)
            target_examples_flip = contrast_examples
            target_ss_flip   = self._sum_similarity(stimuli,
                                                    target_examples_flip,
                                                    param = self.theta_target,
                                                    p=2)
            #End test 110418

            aggregate_flip = target_ss_flip + contrast_ss_flip
            # add baseline similarity

            #Go through each stimulus and calculate their ps
            ps = np.array([])
            for i in range(len(aggregate)):
                    agg_element = np.array([aggregate[i],aggregate_flip[i]])
                    #ps_element = Funcs.softmax(agg_element, theta = self.determinism)
                    ps_element = Funcs.softmax(agg_element, theta = 1.0)
                    ps = np.append(ps,ps_element[0])
                    
        return ps

        

class CopyTweak(Exemplar):
    """
    Continuous implementation of the copy-and-tweak model.
    """

    model = 'Copy and Tweak'
    modelshort = 'CopyTweak'
    modelprint = "Copy & Tweak"
    parameter_names = ['specificity', 'determinism']        
    parameter_rules = dict(
        specificity = dict(min = 0.01),
        determinism = dict(min = 0.01),
        )

    @staticmethod
    def _make_rvs(fmt = dict):
        """ Return random parameters """
        return [np.random.uniform(0.1, 6.0), # specificity
                np.random.uniform(0.1, 6.0), # determinism
        ]
    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):

        # return uniform probabilities if there are no exemplars
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        # get pairwise similarities with target category
        target_examples = self.exemplars[self.assignments == category]
        similarity = self._sum_similarity(stimuli, target_examples)
        # add baseline similarity
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, self.categories[category])
            similarity[known_members] = np.nan
            # get generation probabilities given each source
            ps = Funcs.softmax(similarity, theta = self.determinism)
        elif task == 'assign' or task == 'error':
            # get pairwise similarities with contrast category
            contrast_examples   = self.exemplars[self.assignments != category]
            similarity_flip = self._sum_similarity(stimuli, contrast_examples)
            # add baseline similarity
            
            ps = []
            for i in range(len(similarity)):
                similarity_element = np.array([similarity[i],
                                               similarity_flip[i]])
                ps_element = Funcs.softmax(similarity_element, theta = self.determinism)
                ps = np.append(ps,ps_element[0])


                #self.determinism = max(1e-308,self.determinism)
                
        return ps

class CopyTweakRep(Exemplar):
    """
    Continuous implementation of the copy-and-tweak model, with a representativeness back end.
    """

    model = 'Copy and Tweak Rep'
    modelshort = 'CopyTweakRep'
    modelprint = "Copy & Tweak w/ Rep"
    parameter_names = ['specificity', 'determinism']        
    parameter_rules = dict(
        specificity = dict(min = 0.01),
        determinism = dict(min = 0.01),
        )

    @staticmethod
    def _make_rvs(fmt = dict):
        """ Return random parameters """
        return [np.random.uniform(0.1, 6.0), # specificity
                np.random.uniform(0.1, 6.0), # determinism
        ]
    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):
        # return uniform probabilities if there are no exemplars
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        # get pairwise similarities with target category
        target_examples   = self.exemplars[self.assignments == category]
        similarity_target = self._sum_similarity(stimuli, target_examples)
        #Treat similarity as density estimate (i.e., the likelihoods in representativeness)
        contrast_examples   = self.exemplars[self.assignments != category]
        similarity_contrast = self._sum_similarity(stimuli, contrast_examples)
        representativeness = np.log(similarity_target/similarity_contrast)

        numerator = None
        denom = 0
        if category==self.ncategories:
            ncat = self.ncategories+1
        elif category<self.ncategories:
            ncat = self.ncategories
        else:
            raise Exception('Cannot generate ps from multiple empty categories. Check that get_generation_ps is requesting ps from correct category.')
            
        prior = np.ones(ncat-1) * 1./(ncat-1); #assume uniform -- unlike JK13 we don't have hierarchical structure here?
        ct = 0 #counter for contrast cats
        for c in range(ncat):
            # compute target representativeness
            target_examples = self.exemplars[self.assignments == c]
            contrast_examples   = self.exemplars[self.assignments != c]
            similarity_target = self._sum_similarity(stimuli,target_examples)
            density = similarity_target
            if c == category:
                numerator = density
            else:
                denom += density * prior[ct]
                ct += 1
        representativeness = np.log(numerator/denom)


        # add baseline similarity
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, self.categories[category])
            representativeness[known_members] = np.nan
            # get generation probabilities given each source
            ps = Funcs.softmax(representativeness, theta = self.determinism)
        elif task == 'assign' or task == 'error':
            # get pairwise similarities with contrast category
            #similarity_flip = self._sum_similarity(stimuli, self.categories[1-category])
            representativeness_flip = np.log(similarity_contrast/similarity_target)
            ps = []
            for i in range(len(representativeness)):
                rep_element = np.array([representativeness[i],
                                        representativeness_flip[i]])
                ps_element = Funcs.softmax(rep_element, theta = self.determinism)
                ps = np.append(ps,ps_element[0])


                #self.determinism = max(1e-308,self.determinism)
        return ps


class PackerRep(Exemplar):
    """
    The three-parameter PACKER Model with Representativeness
    """

    model = 'PACKER Rep'
    modelshort = 'PACKERRep'
    modelprint = 'PACKER w/ Rep'
    #parameter_names = ['specificity', 'tradeoff', 'determinism']
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):        

        #040819 Hmm I'm not sure this is the right way to model PACKER-rep after all. Shouldn't we treat the likelihoods in rep as the aggregated sim?
        #Corrected version appears below this commented bit
        # compute target representativeness
        # target_examples = self.exemplars[self.assignments == category]
        # contrast_examples   = self.exemplars[self.assignments != category]
        # similarity_target   = self._sum_similarity(stimuli, target_examples)
        # similarity_contrast = self._sum_similarity(stimuli, contrast_examples)
        # representativeness_target = np.log(similarity_target/similarity_contrast) * self.theta_target
        # representativeness_contrast = np.log(similarity_contrast/similarity_target) * -1.0 * self.theta_cntrst
        # representativeness = representativeness_target + representativeness_contrast
        #can confirm that aggregate_den here and similarity_contrast in copytweakrep are the same (gotta remember to add self.determinism as a factor for similarity_contrast to make them exactly the same)

        numerator = None
        denom = 0
        if category==self.ncategories:
            ncat = self.ncategories+1
        elif category<self.ncategories:
            ncat = self.ncategories
        else:
            raise Exception('Cannot generate ps from multiple empty categories. Check that get_generation_ps is requesting ps from correct category.')
            
        prior = np.ones(ncat-1) * 1./(ncat-1); #assume uniform -- unlike JK13 we don't have hierarchical structure here?
        ct = 0 #counter for contrast cats
        for c in range(ncat):
            # compute target representativeness
            target_examples = self.exemplars[self.assignments == c]
            contrast_examples = self.exemplars[self.assignments != c]
            similarity_target = self._sum_similarity(stimuli,target_examples,param=self.theta_target)
            similarity_contrast = self._sum_similarity(stimuli,contrast_examples,param=-1.0*self.theta_cntrst)
            
            density = similarity_target + similarity_contrast
            #normalize density because if density is negative (which log doesn't like), add min so it becomes positive
            #This is really hacky - might want to reconsider
            #Also note that copytweakrep doesn't do this.
            density = density - np.min(density) + 1e-10
            
            if c == category:
                numerator = density
            else:
                denom += density * prior[ct]
                ct += 1
        representativeness = np.log(numerator/denom)

        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, target_examples)
            representativeness[known_members] = np.nan
            ps = Funcs.softmax(representativeness, theta = 1.0)                       
            #ps = Funcs.softmax(aggregate, theta = self.determinism)                        
        elif task == 'assign' or task == 'error':
            #New test 110418
            #compute contrast and target ss if stimuli is assigned
            #to other cateogry
            #note this code is wrong if ncat > 2
            if self.ncategories>2:
                raise Exception('Cat assignment code for PackerRep not' + 
                                'appropriate for ncat more than 2. Fix it pls.')
            representativeness_flip = self.theta_target*representativeness_contrast - self.theta_cntrst*representativeness_target

            #Go through each stimulus and calculate their ps
            ps = np.array([])
            for i in range(len(representativeness)):
                    rep_element = np.array([representativeness[i],representativeness_flip[i]])
                    #ps_element = Funcs.softmax(agg_element, theta = self.determinism)
                    ps_element = Funcs.softmax(rep_element, theta = 1.0)
                    ps = np.append(ps,ps_element[0])
                    
        return ps

class NPacker(Exemplar):
    """
    The negated three-parameter PACKER Model
    """

    model = 'Negated PACKER'
    modelshort = 'N. PACKER'
    modelprint = 'N. PACKER'
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target','negwt'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        negwt = dict(min=0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
            np.random.uniform(0.01, 10.0) # negwt            
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):
        #New attempt 110418. Updated 170418 - theta_cntrst is for contrast, theta_target is tradeoff for target
        contrast_examples   = self.exemplars[self.assignments != category]
        contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst)
        # compute target sum similarity
        target_examples = self.exemplars[self.assignments == category]
        target_ss   = self._sum_similarity(stimuli, target_examples, param = self.theta_target)
        #End new attempt 110418

        negation = np.zeros(len(stimuli))
        unit_var = 0.001
        #Handle additional empty category
        if category==self.ncategories:
            self.ncategories += 1
        for ci in range(self.ncategories):
            #Only add non-target categories
            if not ci == category:                
                mu,Sigma = self.catStats(ci)
                if self.nexemplars[ci]<2:
                    Sigma = np.eye(self.num_features) * unit_var
                checkzero = np.diagonal(Sigma)==0
                if any(checkzero):
                    #idc = np.diag_indices(self.num_features)
                    replace = checkzero.nonzero()[0]
                    for r in replace:
                        Sigma[r,r] = unit_var
                if np.isnan(Sigma).any() or np.isinf(Sigma).any():
                    #target_dist = np.ones(mu.shape) * np.nan
                    negation = np.ones(len(stimuli)) * np.nan
                else:
                    target_dist = multivariate_normal(mean = mu, cov = Sigma,allow_singular=True) #allowing singular shouldn't be an issue as long as gammas are all created after betas, but might want to tackle this properly someday 120819
                    #target_dist = multivariate_normal(mean = mu, cov = Sigma)
                    if not self.wrap_ax is None:
                        negation += self._wrapped_density(target_dist,stimuli)
                    else:
                        negation += target_dist.pdf(stimuli)
        
        # aggregate target and contrast similarity
        aggregate = contrast_ss + target_ss + (negation * -self.negwt)
        # add baseline similarity
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, target_examples)
            aggregate[known_members] = np.nan
            ps = Funcs.softmax(aggregate, theta = 1.0)                       
            #ps = Funcs.softmax(aggregate, theta = self.determinism)                        
        elif task == 'assign' or task == 'error':
            #New test 110418
            #compute contrast and target ss if stimuli is assigned
            #to other cateogry
            contrast_examples_flip = target_examples
            contrast_ss_flip = self._sum_similarity(stimuli,
                                                    contrast_examples_flip,
                                                    param = -1.0 * self.theta_cntrst)
            target_examples_flip = contrast_examples
            target_ss_flip   = self._sum_similarity(stimuli,
                                                    target_examples_flip,
                                                    param = self.theta_target)
            #End test 110418

            aggregate_flip = target_ss_flip + contrast_ss_flip

            #Go through each stimulus and calculate their ps
            ps = np.array([])
            for i in range(len(aggregate)):
                    agg_element = np.array([aggregate[i],aggregate_flip[i]])
                    #ps_element = Funcs.softmax(agg_element, theta = self.determinism)
                    ps_element = Funcs.softmax(agg_element, theta = 1.0)
                    ps = np.append(ps,ps_element[0])
                    
        return ps


class NCopyTweak(Exemplar):
    """
    Negated Continuous implementation of the copy-and-tweak model.
    """

    model = 'Negated Copy and Tweak'
    modelshort = 'NCopyTweak'
    modelprint = "NCopy & Tweak"
    parameter_names = ['specificity', 'determinism','negwt']        
    parameter_rules = dict(
        specificity = dict(min = 0.01),
        determinism = dict(min = 0.01),
        negwt = dict(min = 0),
        )

    @staticmethod
    def _make_rvs(fmt = dict):
        """ Return random parameters """
        return [np.random.uniform(0.1, 6.0), # specificity
                np.random.uniform(0.1, 6.0), # determinism
                np.random.uniform(0.01, 10.0) # negwt                
        ]
    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False):

        # return uniform probabilities if there are no exemplars
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        # get pairwise similarities with target category
        target_examples = self.exemplars[self.assignments == category]
        similarity = self._sum_similarity(stimuli, target_examples)

        negation = np.zeros(len(stimuli))
        unit_var = 0.001
        #Handle additional empty category
        if category==self.ncategories:
            self.ncategories += 1
        for ci in range(self.ncategories):
            #Only add non-target categories
            if not ci == category:                
                mu,Sigma = self.catStats(ci)
                if self.nexemplars[ci]<2:
                    Sigma = np.eye(self.num_features) * unit_var
                checkzero = np.diagonal(Sigma)==0
                if any(checkzero):
                    #idc = np.diag_indices(self.num_features)
                    replace = checkzero.nonzero()[0]
                    for r in replace:
                        Sigma[r,r] = unit_var
                if np.isnan(Sigma).any() or np.isinf(Sigma).any():
                    negation = np.ones(len(stimuli)) * np.nan
                else:
                    target_dist = multivariate_normal(mean = mu, cov = Sigma,allow_singular=True) #allowing singular shouldn't be an issue as long as gammas are all created after betas, but might want to tackle this properly someday 120819
                    if not self.wrap_ax is None:
                        negation += self._wrapped_density(target_dist,stimuli)
                    else:
                        negation += target_dist.pdf(stimuli)
        
        similarity = similarity + (negation * -self.negwt)
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, self.categories[category])
            similarity[known_members] = np.nan
            # get generation probabilities given each source
            ps = Funcs.softmax(similarity, theta = self.determinism)
        elif task == 'assign' or task == 'error':
            # get pairwise similarities with contrast category
            contrast_examples   = self.exemplars[self.assignments != category]
            similarity_flip = self._sum_similarity(stimuli, contrast_examples)
            # add baseline similarity
            
            ps = []
            for i in range(len(similarity)):
                similarity_element = np.array([similarity[i],
                                               similarity_flip[i]])
                ps_element = Funcs.softmax(similarity_element, theta = self.determinism)
                ps = np.append(ps,ps_element[0])


                #self.determinism = max(1e-308,self.determinism)
                
        return ps
