import abc
import numpy as np

# imports from module
import Modules.Funcs as Funcs


class Model(object):
    """        
    Abstract base class. This is the starting point for all concrete models.
    """
    
    __metaclass__ = abc.ABCMeta
    num_features = 2 #hard code on first init, then update whenever trials come in
    @abc.abstractproperty
    def model(): pass

    @abc.abstractproperty
    def parameter_names(): pass

    @abc.abstractproperty
    def parameter_rules(): pass

    @abc.abstractmethod
    def _make_rvs(): pass

    @classmethod
    def rvs(cls, fmt = dict, **kwargs):
        """
        return random parameters in dict or list format
        """

        params = cls._make_rvs(**kwargs)

        if fmt not in [dict, list]:
            raise Exception('fmt must be dict or list.')
        
        if fmt == list: 
            return params
        else: 
            return dict(zip(cls.parameter_names, params))

    @classmethod
    def clipper(cls, params):
        """
        Clip a set of parameters according to model rules.
        Return data in the same format it arrived.
        """

        # format as list for now
        if not isinstance(params, dict):
            param_dict = cls.params2dict(params)
        else: param_dict = dict(params)

        # clip dict
        for k, rules in cls.parameter_rules.items():
            if rules is None: continue
            if not param_dict.has_key(k): continue
            if 'min' in rules.keys():
                if param_dict[k] < rules['min']:
                    param_dict[k] = rules['min']
            if 'max' in rules.keys():
                if param_dict[k] > rules['max']:
                    param_dict[k] = rules['max']

        # return in original format
        if not isinstance(params, dict):
            return [param_dict[k] for k in cls.parameter_names]
        else: 
            return param_dict


    @classmethod
    def parmxform(cls, params, direction = 1):
        """
        Transform a set of parameters according to model rules.                
        """
        toggle = True #make it a little easier to switch this on or off
        if toggle:
            if not isinstance(params, dict):
                param_dict = cls.params2dict(params)
            else: param_dict = dict(params)

            for k, rules in cls.parameter_rules.items():
                gotmin = False
                gotmax = False
                min = 0
                max = 0
                if rules is None:
                    continue
                if 'min' in rules.keys():
                        gotmin = True
                        min = rules['min']
                if 'max' in rules.keys():
                        gotmax = True
                        max = rules['max']
                if gotmin and gotmax:
                        #Do logit transform scaled to min and max
                        param_dict[k] = Funcs.logit_scale(param_dict[k],min,max,direction = direction)
                elif gotmin:
                        #Do log transform
                        param_dict[k] = Funcs.log_scale(param_dict[k],min,direction = direction)

            # return in original format
            if not isinstance(params, dict):
                return [param_dict[k] for k in cls.parameter_names]
            else: 
                return param_dict
        else:
            return params


    @classmethod
    def params2dict(cls, params):
        """
        Convert list parameters to dict, assuming order set by
        parameter_names. Raises exception if there are not 
        enough params (or too many).
        """

        if len(params) != len(cls.parameter_names):
            S = 'Not enough (or too many) parameters!\nRequired:'
            S += ''.join(['\n\t' + i  for i in cls.parameter_names])
            raise Exception(S)
        return dict(zip(cls.parameter_names, params))
        

    @abc.abstractmethod
    def get_generation_ps(self, stimuli, category, task='generate',seedrng=False): pass

    def __init__(self, categories, params, stimrange=[{'min':-1,'max':1},{'min':-1,'max':1}],stimstep = [.25,.25],wrap_ax=None):
        """
        Initialize the model. "categories" should be a list of numpy
        arrays with the same number of columns (features). Items in 
        "categories" can have unequal number of rows (examples).
                
        'params' is a dict containing all model parameters. 'params'
        should contain an entry for each of the items defined by the 
        'parameter_names' attribute of the concrete class

        'stimrange' is optional, and should ideally be fed into the model from
        the stimrange attribute of a constructed Trialset object. It should
        be a list with length = nfeatures, each element of the list describing
        the min and max of that feature.
        
        'stimstep' is also option and is the increment of each discrete unit on each feature.
                
        """
        
        # force params to dict if it is not one
        if not isinstance(params, dict):
            params = self.params2dict(params)

        # clip parameters into allowed range
        params = self.clipper(params)

        # assign descriptives
        self.categories = [np.atleast_2d(i) for i in categories]
        self.nfeatures = self.categories[0].shape[1]
        self.params = params
        self.stimrange = stimrange
        self.wrap_ax = wrap_ax
        self.stimstep = stimstep
        
        # setup functions
        self._param_handler_()
        self._wrap_ax_handler_()
        self._wts_handler_()
        self._update_()


    def __str__(self):
            S = self.model + ' Model. Current state:' 
            for k in self.parameter_names:
                S += '\n\t' + k + ' = ' + str(getattr(self, k))
            for j in range(self.ncategories):
                S += '\n\t' + 'Category ' +  str(j) + ': ' 
                S += str(self.nexemplars[j]) + ' examples.'
            return S + '\n'

    def _param_handler_(self):
        """ 
        Ensures all the right parameters are in place, and creates
        class attributes based on values.
        """
        for k in self.parameter_names:
            if k not in self.params.keys():
                raise Exception("There is no '" + k + "' parameter!!!")
            else: 
                setattr(self, k, self.params[k])

    def _wrap_ax_handler_(self):
        """
        Ensures wrap_ax is a list of integers or None
        """
        if hasattr(self.wrap_ax,'__len__'):
            if len(self.wrap_ax)==0:
                self.wrap_ax = None

        if not self.wrap_ax is None:
            if not type(self.wrap_ax) is list:
                self.wrap_ax = [self.wrap_ax]

            for wi,wa in enumerate(self.wrap_ax):
                if not type(wa) == int and not wa is None:
                    self.wrap_ax[wi] = int(wa)
                    
    def _wts_handler_(self):
        """
            Sets feature weight parameters for models.
            Raises exception if wts is not the right size.
        """

        if 'wts' not in self.params.keys():
            self.wts = np.ones(self.nfeatures) / self.nfeatures
            return

        if len(self.params['wts']) != self.nfeatures:
            raise Exception("Invalid wts parameter!")

        wts = np.array(self.params['wts'])
        self.wts = wts / float(np.sum(wts))
        self.params['wts'] = self.wts


    def _reset_param_dict_(self):
        """
            Resets self.params given updated values.
        """
        for k in self.params.keys():
            self.params[k] = getattr(self, k)


    def _update_(self):
        """
        Generate descriptives about the known categories. 
        The fields defined below change when items are generated or forgotten,
        so this function is called whenever there is a change to model memory.
        """
        self.ncategories = len(self.categories)
        self.nexemplars = np.array([i.shape[0] for i in self.categories])
        self.exemplars = np.concatenate(self.categories, axis = 0)
        self.assignments = []
        for i in range(self.ncategories):
            self.assignments += [i] * self.nexemplars[i]
        self.assignments = np.array(self.assignments)


    def forget_category(self, category):
        """ Delete an category from the model's memory """
        self.categories.pop(category)
        self._update_()
        

    def simulate_generation(self, stimuli, category, nexemplars = None):
        """
        Simulate the generation of n-exemplars, sourced from stimuli, into a category.
        The resulting category will be added to the model's memory, and the identity 
        of the generated items will be returned.
        """

        if nexemplars is None:
            nexemplars = sum(self.nexemplars)
        # open up the new category if needed
        if category >= self.ncategories:
            self.categories.append(np.empty((0, self.nfeatures)))

        # iterate over examples
        generated_examples = []
        for i in range(nexemplars):

            # compute probabilities, then pick an item
            ps = self.get_generation_ps(stimuli, category)
                        #print sum(ps)-1
            num = Funcs.wpick(ps)
            values = np.atleast_2d(stimuli[num,:])

            # add the item to the category
            if num != None:
                generated_examples.append(num)
                self.categories[category] = np.concatenate(
                    [self.categories[category], values], 
                    axis = 0)                                

            # update knowledge
            self._update_()

        return generated_examples
    
    def catStats(self,category):
        # Get empirical mean and cov
        wrap_ax = self.wrap_ax
        n = self.nexemplars[category]
        if not wrap_ax is None:
            if len(wrap_ax)>1:
                raise Exception('Models cannot handle multiple wrapped axes yet.')
            
            wrap_ax = int(wrap_ax[0])
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
    


class Exemplar(Model):
    """        
    Abstract base class for Exemplar models. Basically this is used to add 
    a function computing summed similarity.
    """
    __metaclass__ = abc.ABCMeta

    def _sum_similarity(self, X, Y, 
        param = 1.0,    
        wts  = None, 
        c = None,
        p = 1):
        """ 
        function to compute summed similarity along rows of 
        X across all items in Y. Resulting array will have one element 
        per row of X.

        the "param" argument acts as a multiplier for similarities prior to summation
        "c" and "wts" can be arbitrary if supplied, or based on the model attribute if not

        p indicates the p-norm for calculating distance in pdist. If p == 1, that's city-block distance. 
        p == 2 indicates Euclidean distance. But really p can take any real positive.

        """
        # set weights and c
        ax_range = self.stimrange[0]['max'] - self.stimrange[0]['min']
        ax_step = self.stimstep[0]
        if wts is None: wts = self.wts
        if c is None: c = self.specificity
        if p == 1:
            distance   = Funcs.pdist(np.atleast_2d(X), np.atleast_2d(Y), w = wts, wrap_ax = self.wrap_ax, ax_range = ax_range, ax_step=ax_step)
        else:
            distance   = Funcs.pdist_gen(np.atleast_2d(X), np.atleast_2d(Y), w = wts, p = p, wrap_ax = self.wrap_ax, ax_range = ax_range, ax_step = ax_step)
        similarity = np.exp(-float(c) * distance)
        similarity = similarity * float(param)
        return np.sum(similarity, axis = 1)

class HierSamp(Model):
    """        
    Abstract base class for hierarchical sampling/Bayesian models (e.g. ConjugateJK13, RepresentJK13). Basically this is used to add 
    a function computing wrapped densities for boundless features.
    """
    __metaclass__ = abc.ABCMeta

    def _wrapped_density(self, target_dist, stimuli,
                         density_ratio_cap = 1e5,
                         maxit = 50):
        """ 
        Function to compute the density on a wrapped space along some axis (like on the surfance of a torus, sphere, cylinder). 
        Only works along one axis at a time for now, though.

        Wrapping stops after the minimum density in one direction is smaller than the maximum density by the ratio
        defined in density_ratio_cap, or after maxit iterations.

        """                                                             
        wrap_ax = self.wrap_ax
        density = target_dist.pdf(stimuli) #Base density
        if not type(wrap_ax) is list:
            wrap_ax = [wrap_ax]
        for ax in wrap_ax:
            #Force wrap_ax to be int (sometimes it's passed as float?!)
            ax = int(ax)
            #Keep taking one set of stimuli above and below the perceived space until ratio is large enough
            stim_ax = stimuli[:,ax]
            stim_unique = np.unique(stim_ax)
            stim_step = np.abs(stim_unique[0]-stim_unique[1])
            stim_diff = np.max(stim_ax) - np.min(stim_ax) + stim_step
            stim_up = stimuli.copy()
            stim_dn = stimuli.copy()
            #Note that this isn't complete if we are wrapping more than 1 axis
            itct = 0
            density_ratio = 1
            maxden = np.max(density)
            while density_ratio < density_ratio_cap and itct < maxit:
                stim_up[:,ax] += stim_diff
                density_up = target_dist.pdf(stim_up)
                maxden = np.max([maxden,np.max(density_up)])
                minden = np.min(density_up)
                density_ratio = maxden/minden
                density += density_up
                itct += 1
                #print('U'+str(itct))
                if itct >= maxit:
                    print('Max wrapped axis reached.')
                #     continue
            #print('itct = ' + str(itct))
            itct = 0
            density_ratio = 1
            while density_ratio < density_ratio_cap and itct < maxit:
                stim_dn[:,ax] -= stim_diff
                density_dn = target_dist.pdf(stim_dn)
                maxden = np.max([maxden,np.max(density_dn)])
                minden = np.min(density_dn)
                density_ratio = maxden/minden
                density += density_dn
                itct += 1
                #print('L'+str(itct))
                if itct >= maxit:
                    print('Max wrapped axis reached.')

            #print('itct = ' + str(itct))
        return density

    def get_musig(self, stimuli, category):
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

