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


	def get_generation_ps(self, stimuli, category, task='generate'):

                # compute contrast sum similarity
                #New attempt 110418. Updated 170418 - theta_cntrst is for contrast, theta_target is tradeoff for target
                contrast_examples   = self.exemplars[self.assignments != category]
                contrast_ss   = self._sum_similarity(stimuli, contrast_examples, param = -1.0 * self.theta_cntrst)
		# compute target sum similarity
		target_examples = self.exemplars[self.assignments == category]
		target_ss   = self._sum_similarity(stimuli, target_examples, param = self.theta_target)
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
                if task is 'generate': 
		        # NaN out known members - only for task=generate
		        known_members = Funcs.intersect2d(stimuli, target_examples)
		        aggregate[known_members] = np.nan
                        ps = Funcs.softmax(aggregate, theta = 1.0)                       
                        #ps = Funcs.softmax(aggregate, theta = self.determinism)                        
                elif task is 'assign' or task is 'error':
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
	# parameter_names = ['specificity', 'determinism', 'baselinesim']
	parameter_names = ['specificity', 'determinism']        
	parameter_rules = dict(
		specificity = dict(min = 1e-10),
		determinism = dict(min = 0.0),
                #baselinesim = dict(min = 0.0),
		)

	@staticmethod
	def _make_rvs(fmt = dict):
		""" Return random parameters """
		return [np.random.uniform(0.1, 6.0), # specificity
			np.random.uniform(0.1, 6.0), # determinism
                        #np.random.uniform(0.1, 6.0)   # baselinesim
                        ]
	def get_generation_ps(self, stimuli, category, task='generate'):
                
		# return uniform probabilities if there are no exemplars
		target_is_populated = any(self.assignments == category)
		if not target_is_populated:
			ncandidates = stimuli.shape[0]
			return np.ones(ncandidates) / float(ncandidates)

		# get pairwise similarities with target category
		similarity = self._sum_similarity(stimuli, self.categories[category])
                # add baseline similarity
                #similarity = similarity + self.baselinesim
                if task is 'generate': 
		        # NaN out known members - only for task=generate
		        known_members = Funcs.intersect2d(stimuli, self.categories[category])
		        similarity[known_members] = np.nan
                        # get generation probabilities given each source
                        ps = Funcs.softmax(similarity, theta = self.determinism)
                elif task is 'assign' or task is 'error':
                	# get pairwise similarities with contrast category
		        similarity_flip = self._sum_similarity(stimuli, self.categories[1-category])
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

class CopyTweakJK13(Exemplar):
	"""
	Continuous implementation of the copy-and-tweak model more akin to 
        Jern & Kemp (2013)'s description
        """
        pass
