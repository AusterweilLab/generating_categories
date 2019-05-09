import numpy as np

# imports from module
import Modules.Funcs as Funcs
from Model import Exemplar


class Packer(Exemplar):
    """
    The three-parameter PACKER Model
    """

    model = 'PACKER'
    modelshort = 'PACKER'
    modelprint = 'PACKER'
    #parameter_names = ['specificity', 'tradeoff', 'determinism', 'baselinesim']
    #parameter_names = ['specificity', 'tradeoff', 'determinism']
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        # tradeoff = dict(min = 0.0, max = 1.0),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        #baselinesim = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            #np.random.uniform(0.0, 1.0),  # tradeoff
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
            #np.random.uniform(0.1, 6.0)   # baselinesim
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False, wrap_ax = None):
        #Get feature ranges for (if) wrapped_axis
        #If no wrap_ax, then it doesn't matter anyway
        ax_range = 2
        ax_step = .25
        if not wrap_ax is None:
            ax_ranges = np.ptp(stimuli,axis=0)
            if not ax_ranges[0]==ax_ranges[1]:
                raise ValueError('Range of x-axis ({}) does not match range of y-axis({})'.format(ax_ranges[0],ax_ranges[1]))
            else:
                ax_range = ax_ranges[0]
            ax_step = abs(stimuli[1,0]-stimuli[0,0]) #assume consistent steps -- dangerous if not the case though
        # compute contrast sum similarity
        #New attempt 110418. Updated 170418 - theta_cntrst is for contrast, theta_target is tradeoff for target
        contrast_examples   = self.exemplars[self.assignments != category]
        contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        # compute target sum similarity
        target_examples = self.exemplars[self.assignments == category]
        target_ss   = self._sum_similarity(stimuli, target_examples, param = self.theta_target,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        #End new attempt 110418
        
        temp_examples = np.array([[-1., -1.,],[1., -1.],[-1,-.75,],[1,-.75]])
        temp_ss   = self._sum_similarity(stimuli, temp_examples, param = -1.0 * self.theta_cntrst,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)


        # # compute contrast sum similarity
        # contrast_examples   = self.exemplars[self.assignments != category]
        # contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 + self.tradeoff)

        # # compute target sum similarity
        # target_examples = self.exemplars[self.assignments == category]
        # target_ss   = self._sum_similarity(stimuli, target_examples, param = self.tradeoff)
        # aggregate target and contrast similarity
        aggregate = contrast_ss + target_ss
        # add baseline similarity
        #aggregate = aggregate + self.baselinesim
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
                                                    wrap_ax=wrap_ax,
                                                    ax_range=ax_range, ax_step=ax_step)
            target_examples_flip = contrast_examples
            target_ss_flip   = self._sum_similarity(stimuli,
                                                    target_examples_flip,
                                                    param = self.theta_target,
                                                    wrap_ax=wrap_ax,
                                                    ax_range=ax_range, ax_step=ax_step)
            #End test 110418

            # #compute contrast and target ss if stimuli is assigned
            # #to other cateogry
            # contrast_examples_flip = target_examples
            # contrast_ss_flip = self._sum_similarity(stimuli,
            #                                         contrast_examples_flip,
            #                                         param = -1.0 + self.tradeoff)
            # target_examples_flip = contrast_examples
            # target_ss_flip   = self._sum_similarity(stimuli,
            #                                         target_examples_flip,
            #                                         param = self.tradeoff)


            aggregate_flip = target_ss_flip + contrast_ss_flip
            # add baseline similarity
            #aggregate_flip = aggregate_flip + self.baselinesim

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
    #parameter_names = ['specificity', 'tradeoff', 'determinism', 'baselinesim']
    #parameter_names = ['specificity', 'tradeoff', 'determinism']
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        # tradeoff = dict(min = 0.0, max = 1.0),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        #baselinesim = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            #np.random.uniform(0.0, 1.0),  # tradeoff
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
            #np.random.uniform(0.1, 6.0)   # baselinesim
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False, wrap_ax=None):
        #Get feature ranges for (if) wrapped_axis
        #If no wrap_ax, then it doesn't matter anyway
        ax_range = 2
        ax_step = .25
        if not wrap_ax is None:
            ax_ranges = np.ptp(stimuli,axis=0)
            if not ax_ranges[0]==ax_ranges[1]:
                raise ValueError('Range of x-axis ({}) does not match range of y-axis({})'.format(ax_ranges[0],ax_ranges[1]))
            else:
                ax_range = ax_ranges[0]
            ax_step = abs(stimuli[1,0]-stimuli[0,0]) #assume consistent steps -- dangerous if not the case though

        # compute contrast sum similarity
        #New attempt 110418. Updated 170418 - theta_cntrst is for contrast, theta_target is tradeoff for target
        contrast_examples   = self.exemplars[self.assignments != category]
        contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst,p=2,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        # compute target sum similarity
        target_examples = self.exemplars[self.assignments == category]
        target_ss   = self._sum_similarity(stimuli, target_examples, param = self.theta_target,p=2,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        #End new attempt 110418
                
        # # compute contrast sum similarity
        # contrast_examples   = self.exemplars[self.assignments != category]
        # contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 + self.tradeoff)

        # # compute target sum similarity
        # target_examples = self.exemplars[self.assignments == category]
        # target_ss   = self._sum_similarity(stimuli, target_examples, param = self.tradeoff)
        # aggregate target and contrast similarity
        aggregate = contrast_ss + target_ss
        # add baseline similarity
        #aggregate = aggregate + self.baselinesim
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
                                                    p=2,
                                                    wrap_ax=wrap_ax,
                                                    ax_range=ax_range, ax_step=ax_step)
            target_examples_flip = contrast_examples
            target_ss_flip   = self._sum_similarity(stimuli,
                                                    target_examples_flip,
                                                    param = self.theta_target,
                                                    p=2,
                                                    wrap_ax=wrap_ax,
                                                    ax_range=ax_range, ax_step=ax_step)
            #End test 110418

            # #compute contrast and target ss if stimuli is assigned
            # #to other cateogry
            # contrast_examples_flip = target_examples
            # contrast_ss_flip = self._sum_similarity(stimuli,
            #                                         contrast_examples_flip,
            #                                         param = -1.0 + self.tradeoff)
            # target_examples_flip = contrast_examples
            # target_ss_flip   = self._sum_similarity(stimuli,
            #                                         target_examples_flip,
            #                                         param = self.tradeoff)


            aggregate_flip = target_ss_flip + contrast_ss_flip
            # add baseline similarity
            #aggregate_flip = aggregate_flip + self.baselinesim

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
    # parameter_names = ['specificity', 'determinism', 'baselinesim']
    parameter_names = ['specificity', 'determinism']        
    parameter_rules = dict(
        specificity = dict(min = 0.01),
        determinism = dict(min = 0.01),
        #baselinesim = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs(fmt = dict):
        """ Return random parameters """
        return [np.random.uniform(0.1, 6.0), # specificity
                np.random.uniform(0.1, 6.0), # determinism
                #np.random.uniform(0.1, 6.0)   # baselinesim
        ]
    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False,wrap_ax=None):
        #Get feature ranges for (if) wrapped_axis
        #If no wrap_ax, then it doesn't matter anyway
        ax_range = 2
        ax_step = .25
        if not wrap_ax is None:
            ax_ranges = np.ptp(stimuli,axis=0)
            if not ax_ranges[0]==ax_ranges[1]:
                raise ValueError('Range of x-axis ({}) does not match range of y-axis({})'.format(ax_ranges[0],ax_ranges[1]))
            else:
                ax_range = ax_ranges[0]
            ax_step = abs(stimuli[1,0]-stimuli[0,0]) #assume consistent steps -- dangerous if not the case though
        
        # return uniform probabilities if there are no exemplars
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        # get pairwise similarities with target category
        similarity = self._sum_similarity(stimuli, self.categories[category],wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        # add baseline similarity
        #similarity = similarity + self.baselinesim
        if task == 'generate': 
            # NaN out known members - only for task=generate
            known_members = Funcs.intersect2d(stimuli, self.categories[category])
            similarity[known_members] = np.nan
            # get generation probabilities given each source
            ps = Funcs.softmax(similarity, theta = self.determinism)
        elif task == 'assign' or task == 'error':
            # get pairwise similarities with contrast category
            similarity_flip = self._sum_similarity(stimuli, self.categories[1-category],wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
            # add baseline similarity
            #similarity_flip = similarity_flip + self.baselinesim
            
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
    # parameter_names = ['specificity', 'determinism', 'baselinesim']
    parameter_names = ['specificity', 'determinism']        
    parameter_rules = dict(
        specificity = dict(min = 0.01),
        determinism = dict(min = 0.01),
        #baselinesim = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs(fmt = dict):
        """ Return random parameters """
        return [np.random.uniform(0.1, 6.0), # specificity
                np.random.uniform(0.1, 6.0), # determinism
                #np.random.uniform(0.1, 6.0)   # baselinesim
        ]
    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False,wrap_ax=None):
        #Get feature ranges for (if) wrapped_axis
        #If no wrap_ax, then it doesn't matter anyway
        ax_range = 2
        ax_step = .25
        if not wrap_ax is None:
            ax_ranges = np.ptp(stimuli,axis=0)
            if not ax_ranges[0]==ax_ranges[1]:
                raise ValueError('Range of x-axis ({}) does not match range of y-axis({})'.format(ax_ranges[0],ax_ranges[1]))
            else:
                ax_range = ax_ranges[0]
            ax_step = abs(stimuli[1,0]-stimuli[0,0]) #assume consistent steps -- dangerous if not the case though
        
        # return uniform probabilities if there are no exemplars
        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        # get pairwise similarities with target category
        similarity_target = self._sum_similarity(stimuli, self.categories[category],wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        #Treat similarity as density estimate (i.e., the likelihoods in representativeness)
        similarity_contrast = self._sum_similarity(stimuli, self.categories[1-category],wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        #print [i*self.determinism for i in similarity_contrast]
        # since number of alternative hypotheses is always 1 if there are a total of 2 categories, p(h') will always be 1, right?
        #prior = 1            
        representativeness = np.log(similarity_target/similarity_contrast)
        # add baseline similarity
        #similarity = similarity + self.baselinesim
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
    #parameter_names = ['specificity', 'tradeoff', 'determinism', 'baselinesim']
    #parameter_names = ['specificity', 'tradeoff', 'determinism']
    parameter_names = ['specificity', 'theta_cntrst', 'theta_target'] 
    parameter_rules = dict(
        specificity = dict(min = 1e-10),
        # tradeoff = dict(min = 0.0, max = 1.0),
        theta_cntrst = dict(min = 0.0),
        theta_target = dict(min = 0.0),
        #baselinesim = dict(min = 0.0),
        )

    @staticmethod
    def _make_rvs():
        """ Return random parameters """
        return [
            np.random.uniform(0.1, 6.0),  # specificity
            #np.random.uniform(0.0, 1.0),  # tradeoff
            np.random.uniform(0.1, 6.0),  # theta_cntrst
            np.random.uniform(0.1, 6.0),  # theta_target
            #np.random.uniform(0.1, 6.0)   # baselinesim
        ] 


    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False,wrap_ax=None):        
        #Get feature ranges for (if) wrapped_axis
        #If no wrap_ax, then it doesn't matter anyway
        ax_range = 2
        ax_step = .25
        if not wrap_ax is None:
            ax_ranges = np.ptp(stimuli,axis=0)
            if not ax_ranges[0]==ax_ranges[1]:
                raise ValueError('Range of x-axis ({}) does not match range of y-axis({})'.format(ax_ranges[0],ax_ranges[1]))
            else:
                ax_range = ax_ranges[0]
            ax_step = abs(stimuli[1,0]-stimuli[0,0]) #assume consistent steps -- dangerous if not the case though

        # compute target representativeness
        target_examples = self.exemplars[self.assignments == category]
        contrast_examples   = self.exemplars[self.assignments != category]

        target_is_populated = any(self.assignments == category)
        if not target_is_populated:
            ncandidates = stimuli.shape[0]
            return np.ones(ncandidates) / float(ncandidates)

        similarity_target   = self._sum_similarity(stimuli, target_examples,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        similarity_contrast = self._sum_similarity(stimuli, contrast_examples,wrap_ax=wrap_ax,ax_range=ax_range, ax_step=ax_step)
        #print similarity_contrast
        representativeness_target = np.log(similarity_target/similarity_contrast) * self.theta_target
        representativeness_contrast = np.log(similarity_contrast/similarity_target) * -1.0 * self.theta_cntrst
        representativeness = representativeness_target + representativeness_contrast
        
        #contrast_ss_num   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst)
        #End new attempt 110418        
        # aggregate target and contrast similarity
        #When I eventually generalize this model to accept more than 2
        #categories, I can use something like this to compute the denominator
        #denom = 0
        #Will need to figure out the prior though?
        # prior = np.ones * 1/self.ncategories; #temp assume uniform
        # for nc in range(self.ncategories):
        #     if nc != category:
        #         contrast_examples = self.exemplars[self.assignments != nc]                
        #         contrast_ss = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst)
        #         target_examples = self.exemplars[self.assignments == nc]                
        #         target_ss = self._sum_similarity(stimuli, target_examples, param = self.theta_target)
        #         denom +=  (target_ss + contrast_ss) * prior[nc]
        # aggregate target and contrast similarity
        #can confirm that aggregate_den here and similarity_contrast in copytweakrep are the same (gotta remember to add self.determinism as a factor for similarity_contrast to make them exactly the same)
        
        # since number of alternative hypotheses is always 1 if there are a total of 2 categories, p(h') will always be 1, right?
        #prior = 1            

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
            # contrast_examples_flip = target_examples
            # contrast_ss_flip = self._sum_similarity(stimuli,
            #                                         contrast_examples_flip,
            #                                         param = -1.0 * self.theta_cntrst)
            # target_examples_flip = contrast_examples
            # target_ss_flip   = self._sum_similarity(stimuli,
            #                                         target_examples_flip,
            #                                         param = self.theta_target)
            #End test 110418

            # #compute contrast and target ss if stimuli is assigned
            # #to other cateogry
            # contrast_examples_flip = target_examples
            # contrast_ss_flip = self._sum_similarity(stimuli,
            #                                         contrast_examples_flip,
            #                                         param = -1.0 + self.tradeoff)
            # target_examples_flip = contrast_examples
            # target_ss_flip   = self._sum_similarity(stimuli,
            #                                         target_examples_flip,
            #                                         param = self.tradeoff)


            #aggregate_flip = target_ss_flip + contrast_ss_flip
            # add baseline similarity
            #aggregate_flip = aggregate_flip + self.baselinesim

            #Go through each stimulus and calculate their ps
            ps = np.array([])
            for i in range(len(representativeness)):
                    rep_element = np.array([representativeness[i],representativeness_flip[i]])
                    #ps_element = Funcs.softmax(agg_element, theta = self.determinism)
                    ps_element = Funcs.softmax(rep_element, theta = 1.0)
                    ps = np.append(ps,ps_element[0])
                    
        return ps

