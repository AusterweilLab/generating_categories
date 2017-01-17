import numpy as np

def histvec(X, bins, density = False):
	D = np.atleast_2d(bins).transpose() - np.atleast_2d(np.array(X)) 
	D = np.abs(D)
	assignment = np.argmin(D, axis=0)
	counts = [np.sum(assignment==i) for i in range(len(bins))]
	counts = np.array(counts)
	
	if density:
	    counts = counts / float(np.sum(counts))
	
	return counts

def cartesian(arrays):
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


def gradientspace(coords, side):
	"""
	Converts a set of coordinates into integer locations within a
	gradient space from 0:side.
	
	In the returned space, the first dimension is the X axis,
	and the second dimension is the Y axis.
	"""
	result = np.array(coords) / 2 + 0.5
	result = result * (side - 1)
	# result = np.fliplr(result)
	return result



def pdist(X, Y, w = np.array([])):
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
	weighted_distance = np.multiply(difference, w)
	return np.sum( np.abs(weighted_distance), axis = 1 )


def add_jitter(points, sd = 0.0001):
	jitter = np.random.normal(loc = 0, scale = sd, size = points.shape);
	return points + jitter