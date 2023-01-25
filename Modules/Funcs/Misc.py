import numpy as np
import sqlite3
import scipy.integrate as integrate
from scipy.spatial import ConvexHull

def stats_battery(betaSet, alphas = None, wrap_ax=None, ax_range=2, ax_step=.25):
    """
    Compute a battery of category stats, return it all in a dict.
    If there is more tha one betaSet (i.e., if it is input as a list of beta categories), then the
    mean statistics across categories are returned.
    """
    #If betaSet is a list, treat each element as a separate category.
    # Otherwise, treat entire betasSet as one category.
    if isinstance(betaSet,list):
        betaSetRun = betaSet
    else:
        betaSetRun = []
        betaSetRun.append(betaSet)

    resSet = []
    for idx, betas in enumerate(betaSetRun):
        res = dict()
        # feature distributions
        res['xrange'], res['yrange'] = np.ptp(betas,axis=0)
        if not wrap_ax is None:
            if not type(wrap_ax) is list:
                wrap_ax = [wrap_ax]            
            for ax in wrap_ax:
                betax = betas[:,ax]
                raw_range = np.max(betax) - np.min(betax)
                #Note formula is different to pdist function, as pdist
                #is only concerned about dist between 2 points. Here, we
                # subtract the largest unoccupied space from the range for
                # the alternate range to compare
                blank_range = np.max(np.diff(np.sort(betax)))
                alt_range = ax_range-blank_range + ax_step
                wrapped_range = np.min([alt_range,raw_range])
                if ax==0:
                    res['xrange'] = wrapped_range
                elif ax==1:
                    res['yrange'] = wrapped_range
                else:
                    raise ValueError('stats_battery function not defined for wrapping third (or higher-dimension) features/axes.')
        
        res['drange'] = res['xrange'] - res['yrange']
        res['xstd'],   res['ystd']   = np.std(betas, axis=0)

        # feature correlation
        res['correlation'] = np.corrcoef(betas, rowvar = False)[0][1]
        if np.isnan(res['correlation']):
            res['correlation'] = 0.0

        # total area of convex hull
        # Only do this if enough data for simplex
        if betas.shape[0]>betas.shape[1]:
            res['area'] = ConvexHull(jitterize(betas, sd = 0.0001)).volume
        else:
            res['area'] = np.nan

        # distances 
        within_mat = pdist(betas, betas)
        res['within'] = np.mean(within_mat[np.triu(within_mat)>0])
        betweendist = [np.mean(pdist(betas,betatemp)) for idxtemp,betatemp in enumerate (betaSetRun) if idx != idxtemp]
        if alphas is not None:
            betweendist.append(np.mean(pdist(alphas,betas)))
        res['between'] = np.mean(betweendist)
        resSet.append(res)
    resmean = {}
    for key in res.keys():
        statlist = []
        for tempres in resSet:
            statlist.append(tempres[key])
        resmean[key] = np.mean(statlist)
    
    return resmean


def BFtt(N,t,r=.707):
    # Calculate Bayes Factor. From Rouder et al. (2009). Outputs BF01 (evidence for the null)
    # N: Sample Size
    # t: t-statistic
    # r: Cauchy prior width
    # Note that while the
    # results seems to match what is shown on Rouder's website (pcl.missouri.edu/bf-one-sample), it doesn't exactly match JASP. Hmm.
    # Possibly JASP uses MCMC so less precise?
    # 090915 - Start coding up, with much trepidation.
    # 010219 - Moved from MATLAB to python
    v = N-1;
    B01numr = (1.+(t**2.)/v)**-((v+1.)/2.);
    
    def B01denmFunc(g):
        out = ((1.+N*g)**(-1./2.)) * ((1. + (t**2.)/((1.+N*g)*v))**-((v+1.)/2.)) * (r*(2.*np.pi)**(-1./2.)) * (g**(-3./2.)) * np.exp(-(r**2.)/(2.*g))
        return out
    
    B01denm = integrate.quad(B01denmFunc,0,np.inf)
    B01 = B01numr/B01denm[0];
    return B01

def ndspace(n, d, low = -1.0, high = 1.0):
    """
    Generate coordinates of points based on an evenly distributed d-dimensional
    grid, sampled at n points along each dimension. User may specify low and high 
    points of grid. Defaults: low = -1, high = +1

    Example: Making a 3-dimensional binary space
    >>> ndspace(2, 3, low = 0)
        [[ 0.  0.  0.]
         [ 0.  0.  1.]
         [ 0.  1.  0.]
         [ 0.  1.  1.]
         [ 1.  0.  0.]
         [ 1.  0.  1.]
         [ 1.  1.  0.]
         [ 1.  1.  1.]]
    """

    # create value vector for all d
    values = [np.linspace(low, high, n)  for i in range(d)]
    return cartesian(values)


def print2dspace(n, op = 'return'):
    """
    Print to the console the arrangment and numbers of 
    elements in an n-by-n space.
    """
    vals = gradientroll(np.arange(n**2), 'roll')[:,:,0]
    if op == 'print':
        print(vals)
    else: 
        return vals


def diffs1D(X, Y):
    """
        Get pairwise differences in 1D
    """
    return np.atleast_2d(X).transpose() - np.atleast_2d(np.array(Y)) 

def histvec(X, bins, density = False):
    """
    MATLAB-like histogram function, with items in vector X being placed
    into the bin with the least difference.

    if density = True, the histogram is normalized.
    """

    D = np.abs(diffs1D(bins, X))
    assignment = np.argmin(D, axis=0)
    counts = [np.sum(assignment==i) for i in range(len(bins))]
    counts = np.array(counts)
    if density: counts = counts / float(np.sum(counts))
    return counts

def permute(xs, low=0):
        """
        Generator that yields a different permutation of elements in a given array
        """
        if low + 1 >= len(xs):
                yield xs
        else:
                for p in permute(xs, low + 1):
                        yield p
                for i in range(low + 1, len(xs)):
                        xs[low], xs[i] = xs[i], xs[low]
                        for p in permute(xs, low + 1):
                                yield p
                        xs[low], xs[i] = xs[i], xs[low]

def cartesian(arrays):
    """
    Generate the cartesian product of input arrays
    """
    la = len(arrays)
    arr = np.empty([len(a) for a in arrays] + [la])
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)


def gradientroll(G, op):
    """
    Conversion of 3D-gradient matrices "G" to 2D column lists,
    and vice-versa.

    gradientroll(G,'roll') will convert a 2D maxtrix G into a 3D array of
    square gradients, the size of which is determined by sqrt(G.shape[0]).
    
    gradientroll(G,'unroll') will turn a square matrix G (which can be
    stacked in 3D) into an array of column vectors (one for each 3D slice).
    """

    # convert matrix into vector
    if op == 'unroll':

        # ensure G is 3D
        if G.ndim == 2:
            G = G[:,:,None]

        ngradients, nelements = G.shape[2], G.shape[0]*G.shape[1]
        return np.reshape(np.flipud(G),[nelements,ngradients]);

    # convert a column matrix into a set of 2d matrices
    elif op == 'roll':
        
        # ensure G is a 2D column vector
        if G.ndim == 1:
            G = np.atleast_2d(G).T

        side, ngradients = int(np.sqrt(G.shape[0])), int(G.shape[1])
        return np.flipud(np.reshape(G, (side, side, ngradients) ))


def pdist(X, Y, w = np.array([]), wrap_ax = None, ax_range = 2, ax_step = .25):
    """
    Calculate weighted city-block distance between two ND arrays
    
    Parameters
    ----------
    X, Y: 2D arrays containing rows to be compared.
        X and Y must have the same number of columns.
        Distance is computed between rows of X and Y
    w (optional): 1D array of column weights. 
        Must contain 1 value per column of X and Y. 
        Should sum to 1, but this is not enforced.
        If w is not provided, all weights are set at 1/ncols
    Returns an nX-by-nY array of weighted city-block distance.
    
    wrap_ax indicates which axis is boundless (i.e., take the shortest of either the distance or max-distance)

    ax_range is the limits of both axes

    ax_step is the unit-size of each step (assumed to be same across all axes)

Examples
    --------
    >>> X = np.array([[0,0],[0,1]])
    >>> Y = np.array([[1,0],[1,1]])
    >>> pdist(X,Y)
    array([[ 0.5  1. ]
           [ 1.   0.5]])
    >>> w = np.array([0, 1])
    >>> pdist(X,Y,w)
    array([[0 1]
           [1 0]])
    """

    # get info
    nX, nY, ncols =  X.shape[0], Y.shape[0], X.shape[1]

    # uniform weights if not otherwise provided
    if not w.size:
        w = np.array([1.0/ncols for i in range(ncols)])

    # tile to common sizes
    X = np.tile(X[:,:,None], (1,1,nY) )
    Y = np.tile(np.swapaxes(Y[:,:,None],0,2),(nX,1,1))
    w = w[None,:,None]
    # compute distance
    difference = X - Y
    #If any axis is boundless, take its minimum of either d or max-d
    if not wrap_ax is None:
        if not type(wrap_ax) is list:
            wrap_ax = [wrap_ax]
        #print('Old diff: {}'.format(difference[:,1]))
        for ax in wrap_ax:
            #Ensure ax is int of some sortif not None
            if not ax is None:
                ax = int(ax)
                diff_ax = np.abs(difference[:,ax].copy())
                diff_alt = ax_range-diff_ax + ax_step
                diff_min = np.min([diff_ax,diff_alt],axis=0)
                difference[:,ax] = diff_min
        #print('New diff: {}'.format(difference[:,ax]))

    weighted_distance = np.multiply(difference, w)
    return np.sum( np.abs(weighted_distance), axis = 1 )

def pdist_gen(X, Y, w = np.array([]), p = 2,wrap_ax = None,ax_range = 2,ax_step = .25):
    """
    Calculate generalised weighted distance between two ND arrays.
    
    Parameters
    ----------
    X, Y: 2D arrays containing rows to be compared.
        X and Y must have the same number of columns.
        Distance is computed between rows of X and Y
    w (optional): 1D array of column weights. 
        Must contain 1 value per column of X and Y. 
        Should sum to 1, but this is not enforced.
        If w is not provided, all weights are set at 1/ncols
    p (defaults to 2): p-norm to determine distance metrice. If
        p == 1 is Manhattan (or city-block)
        p == 2 is Euclidean

    Returns an nX-by-nY array of weighted distance.

    wrap_ax indicates which axis is boundless (i.e., take the shortest of either the distance or max-distance)

    ax_range is the limits of both axes (assumed to be same across all axes)
    
    ax_step is the unit-size of each step (assumed to be same across all axes)
    
    Examples
    --------
    >>> X = np.array([[0,0],[0,1]])
    >>> Y = np.array([[1,0],[1,1]])
    >>> pdist(X,Y)
    array([[ 0.5  1. ]
           [ 1.   0.5]])
    >>> w = np.array([0, 1])
    >>> pdist(X,Y,w)
    array([[0 1]
           [1 0]])
    """

    # get info
    nX, nY, ncols =  X.shape[0], Y.shape[0], X.shape[1]

    # uniform weights if not otherwise provided
    if not w.size:
        w = np.array([1.0/ncols for i in range(ncols)])

    # tile to common sizes
    X = np.tile(X[:,:,None], (1,1,nY) )
    Y = np.tile(np.swapaxes(Y[:,:,None],0,2),(nX,1,1))
    w = w[None,:,None]
    # compute distance
    difference = X - Y
    #If any axis is boundless, take its minimum of either d or max-d
    if not wrap_ax is None:
        if not type(wrap_ax) is list:
            wrap_ax = [wrap_ax]
        for ax in wrap_ax:
            #Ensure ax is int of some sort
            ax = int(ax)
            diff_ax = np.abs(difference[:,ax].copy())
            diff_alt = ax_range-diff_ax + ax_step
            diff_min = np.min([diff_ax,diff_alt],axis=0)
            difference[:,ax] = diff_min

    weighted_distance = np.multiply(difference, w)
    return np.power(np.sum( weighted_distance**p, axis = 1 ),1./p) #Euclidean, so sqrt the summed sq distance

def aic(loglike,nparms):
        aic = 2.0*nparms - 2.0* (-1.0 * loglike)
        return aic


def jitterize(points, sd = 0.0001):
    """
    Add a small amount of jitter to points.
    """
    jitter = np.random.normal(loc = 0, scale = sd, size = points.shape);
    return points + jitter


def wpick(ps):
    """
    Function to pick from a set a probabilities.
        
    """
    #Deal with negative ps - return None?
    ps = np.array(ps)
    if any(ps<0):
        #pslin = ps.reshape((-1,ps.size)).flatten
        #ps = ps/sum(pslin)
        return None
    else:
        return np.random.choice(range(len(ps)), p = ps)

def intersect2d(X, Y):
    """
    Function to find intersection of two arrays.
    Returns index of rows in X that exist in Y.
    """
    X = np.tile(X[:,:,None], (1, 1, Y.shape[0]) )
    Y = np.swapaxes(Y[:,:,None], 0, 2)
    Y = np.tile(Y, (X.shape[0], 1, 1))
    eq = np.all(np.equal(X, Y), axis = 1)
    eq = np.any(eq, axis = 1)
    return np.nonzero(eq)[0]


def softmax(X, theta = 1.0, axis = None, toggle = True):
    """
    Compute the softmax of each element along an axis of X.

    Parameters
    ----------
    X: ND-Array. NaN values will have probability 0.
    theta (optional): float parameter, used as a multiplier
        prior to exponentiation. Default = 1.0
    axis (optional): axis to compute values along. Default is the 
        first non-singleton axis.

    Returns an array the same size as X. The result will sum to 1
    along the specified axis.

        toggle: If True, calculates soft max (exponentiated Luce)
                If False, calculates regular Luce choice model

    Examples
    --------
    >>> X = np.array([[1,2,3], [5,3,1]])
    >>> softmax(X, theta = 0.5, axis = 0)
            [[ 0.12  0.38  0.73]
              [ 0.88  0.62  0.27]]
    >>> softmax(X, theta = 0.5, axis = 1)
            [[ 0.19  0.31  0.51]
             [ 0.67  0.24  0.09]]
    """

    # make X at least 2d
    y = np.atleast_2d(X)

    # find axis
    if axis is None:
        axis = next(j[0] for j in enumerate(y.shape) if j[1] > 1)

    # multiply y against the theta parameter, 
    # then subtract the max for numerical stability
    y = y * float(theta)

        
    
    # exponentiate y, then convert nans into 0
    if toggle:
        y = y - np.expand_dims(np.nanmax(y, axis = axis), axis)
        y = np.exp(y)
    

        
        
    y[np.isnan(y)] = 0.0

    # take sum along axis, divide elementwise
    ax_sum = np.expand_dims(np.sum(y, axis = axis), axis)
    if ax_sum==0:
        p = np.zeros(y.shape)#p = np.array([0])
    else:
        p = y / ax_sum
        
        
    # flatten if X was 1D
    if len(X.shape) == 1:
        p = p.flatten()


    return p

def luce(X, theta = 1.0, axis = None, toggle = True):
    """
        Return result of Luce's choice rule given some list of X.
        This is softmax without exponentiation.

    Parameters
    ----------
    X: ND-Array. NaN values will have probability 0.
    theta (optional): float parameter, used as a multiplier
        . Default = 1.0
    axis (optional): axis to compute values along. Default is the 
        first non-singleton axis.

    Returns an array the same size as X. The result will sum to 1
    along the specified axis.

        toggle: If True, calculates soft max (exponentiated Luce)
                If False, calculates regular Luce choice model

    Examples
    --------
    >>> X = np.array([[1,2,3], [5,3,1]])
    >>> luce(X, theta = 0.5, axis = 0)
            [[ 0.12  0.38  0.73]
              [ 0.88  0.62  0.27]]
    >>> luce(X, theta = 0.5, axis = 1)
            [[ 0.19  0.31  0.51]
             [ 0.67  0.24  0.09]]
    """

    # make X at least 2d
    y = np.atleast_2d(X)

    # find axis
    if axis is None:
        axis = next(j[0] for j in enumerate(y.shape) if j[1] > 1)

    # multiply y against the theta parameter, 
    # then subtract the max for numerical stability
    y = y * float(theta)

        
    
    # exponentiate y, then convert nans into 0
        # if toggle:
        #         y = y - np.expand_dims(np.nanmax(y, axis = axis), axis)
        #         y = np.exp(y)            
        
    y[np.isnan(y)] = 0.0

    # take sum along axis, divide elementwise
    ax_sum = np.expand_dims(np.sum(y, axis = axis), axis)
    if ax_sum==0:
        p = np.zeros(y.shape)
    else:
        p = y / ax_sum
        
        
    # flatten if X was 1D
    if len(X.shape) == 1:
        p = p.flatten()


    return p

#Logit function
def logit_scale(x, min=0, max=1, direction=1):
        """
        Logit function. Useful for squeezing real number line between 0 and 1.
        
        Set direction to 1 for regular, or -1 for inverse.
        """
        range = max-min
        if direction == 1:
                #Scale range of x to 0 and 1
                x = (np.array(x) - min)/float(range)
                xed = np.log(x/(1-x)) #xed meaning transformed
                return xed
        elif direction == -1:
                x = 1/(1+np.exp(-x))
                xed = x * range + min
                return xed

#Log transformation function
def log_scale(x, bound = 0, direction = 1):
        """
        Log transformation function. Adjusts for the bound (i.e.,
        the min or max doesn't need to be 0). 
        Direction with 1 is regular, and -1 is reverse.
        """
        if direction == 1:
                x = np.array(x)-bound
                xed = np.log(x)
                return xed
        elif direction == -1:
                x = np.exp(x)
                xed = bound+x
                return xed

        
# Validate input
def valInput(s,options):
        """
        valInput prompts the user for some input with message
        's', giving some list of possible options 'options'.

        If valid input is supplied by the user, the selected
        index is returned. If invalid, empty string and
        negative index is returned.

        's' must be a string
        'options' must be a list of strings

        User must supply an integer as input
        090218 : SX start

        """
        prints = s + '\n'
        ct = 0
        for i in options:
                prints += '[' + str(ct) + '] ' + i + '\n'
                ct += 1
        try:
                outi = int(raw_input(prints))                
                outs = options[outi]
        except KeyboardInterrupt:
                import sys
                sys.exit()
        except:
                outi = -1
                outs = ''

        return outi

        
def valData(ins,s,options,tries = 5):
        """
        Checks if the supplied INS is a valid option among OPTIONS. Otherwise,
        prompt user with S. 

        """
        if ins in options:
                outi = options.index(ins)
        else:        
                outi = valInput(s,options)

        outs = options[outi]
        tries -= 1
        if tries <=0:
                raise Exception('Please try again and then select an appropriate option.'+\
                                '\nIt\'s really not that hard.\n')        
        if outi<0:
                outs = valData(ins,s,options,tries)                
                
        return outs

def getMatch(match,db='../cat-assign/data_utilities/cmp_midbot.db',fetch='Old'):
        """
        Fetch the Old and Matched participant number given some database. 
        Matches to the matched ppt number by default (i.e., fetches the old ppt number).
        """
        conn  = sqlite3.connect(db)
        
        #Use cursor method to get data, since it doesn't seem to like sqlite3 for some reason
        c = conn.cursor()
        c.execute('SELECT * FROM stimuli')
        data = c.fetchall();
        dataA = np.array(data);
        uniquePpt = np.unique(dataA[:,0]);        
        ar = [[int(ppt),int(dataA[dataA[:,0]==ppt,1][0])] for ppt in uniquePpt]
        #uniquePpt = [[row[0],row[1]] for i,row in enumerate(data) if row[0] != data[max(i-1,0)][0]] #whoo. Ugly, but works! Actually no it doesn't. It leaves out index 0:(
        ar = np.array(ar)
        #sort this
        ar = ar[ar[:,0].argsort()]
        if fetch == 'Old':
                matchCol = 0 #Match
                fetchCol = 1
        else: #if fetch == 'New':
                matchCol = 1
                fetchCol = 0

        if match=='all':
                out = ar
        else:
                row = ar[ar[:,matchCol]==match,:]
                row = row.squeeze()
                if len(row)>0:
                        out = row[fetchCol]
                else:
                        out = [];

        return out
    
def getCatassignID(inID,source='analysis',fetch='old'):
    '''
    #Fetch participant IDs from the catassign experiment (similar to getMatch, but takes
    # data from the constructed catassign_pptID pickle made from make_participant_database.py
    # in the cat-assign/analysis folder.
    # source and fetch can be any of 'old','match','analysis', or 'assigned'
    # Input can be any integer or 'all' (which returns a list), or a list.
    '''
    import pickle
    file  = 'pickles/catassign_pptID.p'
    with open(file,'rb') as f:
        data = pickle.load(f)
    if isinstance(inID,int):
        out = data.loc[data[source] == inID][fetch].item()        
    elif inID is 'all':
        out = list(data[source])
    elif hasattr(inID,'__len__'):
        out = []
        for i in inID:
            out += [data.loc[data[source] == i][fetch].item()]
    #Make sure that only ints are returned
    if isinstance(out,float):
        out = int(out)
    elif isinstance(out,list):
        out = [int(i) if not np.isnan(i) else np.nan for i in out]
        
    return out
    
    
#Function to print iteration progress nicely
def printProg(i,print_ct = 0, steps = 1, breakline = 40, breakby = 'char'):
        """
        Prints progress of some iterator at every STEP, with line breaks defined
        by BREAKLINE. BREAKBY can be 'char', which breaks lines by the number of
        character spaces or columns defined in BREAKLINE, or BREAKBY can be
        'mult', which breaks lines every multiple of BREAKLINE

        Note that if BREAKBY is 'char', a counter should be initialised outside this function
        """
        import sys
        import numpy as np
        if np.mod(i,steps)==0:
                if breakby == 'char':
                        if not 'print_ct' in locals():
                                raise Exception('breakby is set to \'char\', so print_ct must be defined.')
                        #Length of current char
                        leni = len(str(i))
                        if print_ct + leni > breakline:
                                #Line break
                                print(i)
                                print_ct = 0
                        else:
                                #No line break
                                print(i,end="")
                                sys.stdout.flush()                                
                                print_ct += leni+1
                
                elif breakby == 'mult':
                        if np.mod(i,breakline) != 0:
                                #No line break
                                print(i,end="")
                                sys.stdout.flush()
                        elif i>0:
                                #Line break
                                print(i)
                else:
                        raise Exception('Please specify breakby as either \'char\' or \'mult\'.')
        return print_ct

def getrange(stimuli):
    '''
    Get the min and max for each stimulus feature. To be used when initialising models.
    Also return the steps of each dimension
    '''
    stimrange = []
    for i in range(len(stimuli[0])):
        stimrange += [{'min': stimuli[:,i].min(),
                       'max': stimuli[:,i].max()}]
        
    ndim = stimuli.shape[1]
    stimstep = []
    for di in range(ndim):
        uniques = np.unique(stimuli[:,di])
        st = uniques[1]-uniques[0]
        stimstep += [st]

    return stimrange,stimstep
        

    
def getModelName(modelname,fetch='short'):
    '''
    Fetches the specified model name. FETCH can be 'short',long','class'.
    '''
    execfile('Imports.py')
    from Modules.Classes import CopyTweak
    from Modules.Classes import Packer
    from Modules.Classes import ConjugateJK13
    from Modules.Classes import RepresentJK13
    from Modules.Classes import CopyTweakRep
    from Modules.Classes import PackerRep
    from Modules.Classes import PackerEuc
    from Modules.Classes import NegatedSpace
    from Modules.Classes import NConjugateJK13
    from Modules.Classes import NRepresentJK13
    from Modules.Classes import NPacker
    from Modules.Classes import NCopyTweak

            
    model_keywords = dict()
    modelnames = dict()
    models = [Packer,CopyTweak,ConjugateJK13,RepresentJK13,CopyTweakRep,PackerRep,PackerEuc,
              NegatedSpace,NConjugateJK13,NRepresentJK13,NPacker,NCopyTweak]
    #Set everything to lowercase
    modelname = modelname.lower()
    #First, add default names
    for model in models:
        modelnames[model.__name__] = [model.modelshort, model.model, model.__name__]
        model_keywords[model.__name__] = [model.modelshort.lower(), model.model.lower(), model.__name__.lower()]
    #Then add some base or keywords for each model
    model_keywords['Packer'] += ['pack']
    model_keywords['PackerRep'] += ['pr','packrep']
    model_keywords['CopyTweak'] += ['copy','cp','c&t','cnt']
    model_keywords['CopyTweakRep'] += ['ctr','copyrep']
    model_keywords['ConjugateJK13'] += ['cjk13','conjugate','hierarchical']
    model_keywords['RepresentJK13'] += ['rjk13','rep','represent']
    #Parse the fetch type
    fetchtypes = ['short','long','class']
    fetchidx = fetchtypes.index(fetch)
    #Then try to identify the requested model
    fetchmodel = ''    
    for model in model_keywords.keys():        
        if modelname in model_keywords[model]:
            fetchmodel = modelnames[model][fetchidx]
            return fetchmodel
            
    
def get_initials(input,num_letters = 1,include_delim = True):
    '''
    Extracts the first num_letters of every word in a string. Treats underscores as delimiters.
    '''
    import re
    if include_delim:
        delim = re.findall('[\s+_]',input)
        delim += [''] #last delimiter is blank
        output = "".join(item[0:num_letters]+delim[i] for i,item in enumerate(re.findall("[a-zA-Z0-9]+", input)))
    else:
        output = "".join(item[0:num_letters] for item in re.findall("[a-zA-Z0-9]+", input))
    return output

##Sorry, don't mean to clog things up here but for convenience I'm dumping more misc functions here
def get_corr(start_params,pptdata,tso,model_obj,fixedparams=None,pearson=True,print_on = False, parmxform = False, return_ll = False):
    """
    Returns the correlation between model fits (to generation probabilities) and observed participant error in the
    catassign data (experiment 3). start_params is the set of parameter values, pptdata and tso can be obtained through
    the prep_corrvar function.

    """
    execfile('Imports.py')
    import Modules.Funcs as funcs
    from Modules.Classes import ConjugateJK13
    from Modules.Classes import RepresentJK13
    import pandas as pd
    import math
    import numpy as np
    from scipy.stats import stats as ss
    #convert free parms to dict
    if not type(start_params) is dict:
        start_params = model_obj.params2dict(start_params)        

    # extract fixed parameters and feed it into start_params variable
    if hasattr(fixedparams,'keys'):
        for parmname in fixedparams.keys():
            start_params[parmname] = fixedparams[parmname]

    
    #Get log likelihoods
    ll_list = []
    print_ct = 0
    for pi,pptdatarow in pptdata.iterrows():
        params = start_params.copy()        
        params['wts'] = pptdatarow['ppt_att']
        if model_obj ==  ConjugateJK13 or model_obj == RepresentJK13:
            params['wts'] = 1.0 - params['wts']
        #Initialise model (the value of the arguments here don't really matter)
        model = model_obj(np.array([[0,0]]), params)
        #pptdata = pd.DataFrame(columns = ['condition','betas'])
        if parmxform:
            #transform parms    
            params = model.parmxform(params, direction = 1)
        tso_ppt = tso[pi]
        raw_array = []#np.zeros((1,nbetapermute))#np.zeros((nstim,nbetapermute))
        for tso_ppti in tso_ppt:
            #the neg loglikelihoods can get really large, which will tip it over to Inf when applying exp.
            # To get around this, divide the nLL by some constant, exp it, add it to the prev prob, then log,
            # and add it to the log of the same constant
            raw_array_ps = tso_ppti.loglike(params,model_obj)
            raw_array += [raw_array_ps]
            
        raw_array_sum = np.array(raw_array) #raw_array.sum(0)    
        raw_array_sum_max = raw_array_sum.max()
        raw_array_t = np.exp(-(raw_array_sum - raw_array_sum_max)).sum()
        raw_array_ll = -np.log(raw_array_t) + raw_array_sum_max
        ll_list += [raw_array_ll]
        if print_on:
            #Print progress
            print_ct = funcs.printProg(pi,print_ct,steps = 1, breakline = 20, breakby = 'char')            

    #ll_list = np.atleast_2d(ll_list)
    error_list = pptdata.ppterror.as_matrix()
    if pearson:
        corr = ss.pearsonr(ll_list,error_list)
    else:        
        corr = ss.spearmanr(ll_list,error_list)

    r = corr[0] * -1.0
    #p = corr[1]

    if return_ll:
        return ll_list
    else:
        return r




def prep_corrvar(info,assignment,stimuli,stats,WT_THETA=1.5,print_on=True):
    """
    Prepares variables to be used in get_corr
    """
    execfile('Imports.py')
    import Modules.Funcs as funcs
    from Modules.Classes import Simulation
    import pandas as pd
    import math
    import numpy as np
    from scipy.stats import stats as ss

    #Generate a list of all participant errors and their attention_weights
    pptdata = pd.DataFrame(columns=['pptmatch','ppterror','ppt_att'])
    #Prepare all trialset objects in the order of pptdata
    tso = []
    print_ct = 0
    print('Preparing trialset objects for each participant. This could take a couple of minutes.')
    for i,row in info.iterrows():
        ppt = row.participant
        pptAssign = assignment.loc[assignment['participant']==ppt].sort_values('trial')
        nTrials = len(pptAssign)
        accuracyEl = float(sum(pptAssign.correctcat == pptAssign.response))/nTrials
        pptmatch = row.pptmatch
        #Compute and add weights
        pptOld = funcs.getCatassignID(pptmatch,source='match',fetch='old')
        ranges = stats[['xrange','yrange']].loc[stats['participant']==pptOld]
        #Find alphas and betas
        pptloc = info['pptmatch']==pptmatch
        #Get alphas with an ugly line of code
        alphas  = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[0:4];
        betas = eval(info['stimuli'].loc[pptloc].as_matrix()[0])[4:8];        
        pptdata = pptdata.append(
            dict(pptmatch = pptmatch, ppterror = 1-accuracyEl,
                 ppt_att = funcs.softmax(-ranges, theta = WT_THETA)[0]),            
            ignore_index=True
        )

        #Add trialsetobj
        alpha_vals = stimuli[alphas,:]
        nstim = len(betas)
        # Get all permutations of pptbeta and make a new trialObj for it
        nbetapermute = math.factorial(nstim)
        betapermute = [];
        raw_array = np.zeros((1,nbetapermute))#np.zeros((nstim,nbetapermute))
        tso_ppt = []
        for beta in funcs.permute(betas):
            categories = alphas
            trials = range(nstim)
            pptDF = pd.DataFrame(columns = ['participant','stimulus','trial','categories'])
            pptDF.stimulus = pd.to_numeric(pptDF.stimulus)
            #Initialise trialset object
            pptTrialObj = Simulation.Trialset(stimuli)
            pptTrialObj.task = 'generate'
            for trial,beta_el in enumerate(beta):
                    pptDF = pptDF.append(
                            dict(participant=pptmatch, stimulus=beta_el, trial=trial, categories=[categories]),ignore_index = True
                    )
            pptTrialObj.add_frame(pptDF)
            tso_ppt += [pptTrialObj]
        tso += [tso_ppt]
        if print_on:
            print_ct = funcs.printProg(i,print_ct,steps = 1, breakline = 20, breakby = 'char')
            
    return pptdata,tso

def compress_chtc_parms(best_params_t):
    '''
    Rebuilds the best_params data from chtc gs fits into something that the
    analysis scripts can use more easily .
    '''
    #Rebuild it into a smaller dict
    best_params = dict()
    for modelname in best_params_t.keys():    
        best_params[modelname] = dict()
        for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
            parmval = best_params_t[modelname]['bestparmsll']
            best_params[modelname][parmname] = parmval[i]

    return best_params

def mvgamma(p,a):
    #Multivariate Gamma function
    from scipy.special import gamma
    import numpy as np
    if p == 1:
        out = gamma(a)
    elif p > 1:
        out = (np.pi**((p-1)/2.)) * gamma(a) * mvgamma(p-1,a-(1/2.))
    return out

        
def invwishartpdf(X,scale,nu):
    #Weirdly, it looks like the default scipy.stats invwishart doesn't like the df (nu) being less than the number of dimensions p, even though wikipedia says that's ok as long as it's more than p-1? This is my attempt at producing invwishart pdfs without that constraint. Really basic stuff though - doesn't currently do any checks that the scale or psi are positive definite etc.
    from numpy.linalg import det
    import numpy as np
    p = scale.shape[0]
    if nu<p-1:
        raise ValueError('The value of nu (%.3f) cannot be lower than the number of dimensions of scale matrix (%d) minus one.' % (nu,p))
    numerator = det(scale)**(nu/2.)
    denom = (2**(nu*p/2.)) * mvgamma(p,nu/2.)
    x_co = det(X) ** (-(nu+p+1.)/2.)
    #x_co_inv = det(X) ** ((nu+p+1.)/2)
    #denom = (2**(nu*p/2)) * mvgamma(p,nu/2)
    xinv = np.linalg.inv(X)
    e_co = np.exp(-1/2. * np.trace(np.matmul(scale,xinv)))
    tr = np.trace(np.matmul(scale,xinv))
    
    out = numerator/denom * x_co * e_co #numerator/denom/x_co * e_co #numerator/denom * x_co * e_co
    return out

## A bunch of convex hull-related functions follow
class Line(object):
    #Get the equation of the line crossing pointA and pointB
    #Assuming 2-dimensions for simplicity
    #First argument can also be nparray or list containing the two points
    def __init__(self,pointA,pointB=None):
        if pointB is None and len(pointA)==2:
            pointB = pointA[1]
            pointA = pointA[0]
        self.points = np.array([pointA,pointB])
        self.eq = self.mc(self.points)
        self.xs = np.array([pointA[0],pointB[0]])
        self.ys = np.array([pointA[1],pointB[1]])
    def mc(self,points):
        A = np.array(points[0],dtype=float)
        B = np.array(points[1],dtype=float)
        diff = A-B
        if diff[0]==0:
            m = np.inf
            c = None
        else:
            m = diff[1]/diff[0]
            c = A[1] - m*A[0]
        return (m,c)
    
    def checkxy(self,x,y,line2):
        #Check that x- and y-value of intercept lies within ranges of lines 
        yr1 = self.ys
        yr2 = line2.ys
        yrs = [yr1,yr2]
        for yr in yrs:
            if y<min(yr)or y>max(yr):
                return False
        
        xr1 = self.xs
        xr2 = line2.xs
        xrs = [xr1,xr2]
        for xr in xrs:
            if x<min(xr)or x>max(xr):
                return False
        #If all good, return True
        return True

def intersect(line1,line2):
    #Get the intersect between two lines
    #If it doesn't exist within the ranges of the lines, return None
    #line1 and line2 are line Objects created with Line(pointA,pointB)    
    m1,c1 = line1.eq
    m2,c2 = line2.eq 
    #if m's are equal, they're parallel and will never intersect
    if m1==m2:
        return(None,None)
    #Handle straight verticals
    if np.isinf(m1) and np.isinf(m2):
        return(None,None)
    elif np.isinf(m1):
        x = line1.xs[0]
        y = m2*x + c2
        if line1.checkxy(x,y,line2):  
            return np.array((x,y))
        else:
            return (None,None)        
    elif np.isinf(m2):
        x = line2.xs[0]
        y = m1*x + c1
        if line2.checkxy(x,y,line1):  
            return np.array((x,y))
        else:
            return (None,None) 
    
    #Otherwise, derive x and y accordingly
    x = (c2-c1)/(m1-m2)  
    y = m1*x + c1
    if line1.checkxy(x,y,line2):  
        return np.array((x,y))
    else:
        return (None,None)
    
def isinhull(hull,point):
    #Check if point is within the hull
    #If point changes the vertices of the hull, return false
    points = hull.points
    newpoints = np.concatenate([points,[point]])
    newhull = ConvexHull(newpoints)
    pold = points[hull.vertices]
    pnew = newpoints[newhull.vertices]
    if not len(pold) == len(pnew):
        return False
    else: 
        #If same length, test for equivalence across all elements
        if np.all(pold == pnew):
            return True
        else:
            return False

def overlapArea(cat1,cat2):
    hull1 = ConvexHull(cat1)
    hull2 = ConvexHull(cat2)

    verts1 = np.concatenate((cat1[hull1.vertices],[cat1[hull1.vertices[0]]]),axis=0)
    lines1 = [Line(pt,verts1[pi+1]) for pi,pt in enumerate(verts1) if pi<len(verts1)-1]

    verts2 = np.concatenate((cat2[hull2.vertices],[cat2[hull2.vertices[0]]]),axis=0)
    lines2 = [Line(pt,verts2[pi+1]) for pi,pt in enumerate(verts2) if pi<len(verts2)-1]

    #Get intersections
    ints = []
    for l1 in lines1:
        for l2 in lines2:
            (x,y) = intersect(l1,l2)
            if not x is None:
                ints += [intersect(l1,l2)]

    #For each vertex, check if it's contained within the other hull
    inVerts = []
    for p in cat1[hull1.vertices]:
        if isinhull(hull2,p):
            inVerts += [p]

    for p in cat2[hull2.vertices]:
        if isinhull(hull1,p):
            inVerts += [p]

    overVerts = ints+inVerts
    
    if len(overVerts)>0:
        hullOver = ConvexHull(overVerts)
        return hullOver.volume
    else:
        return 0
