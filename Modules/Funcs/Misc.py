import numpy as np
from scipy.spatial import ConvexHull

def stats_battery(betas, alphas = None):
	"""
	Compute a battery of category stats, return it all in a dict
	"""
	res = dict()

	# feature distributions
	res['xrange'], res['yrange'] = np.ptp(betas,axis=0)
	res['drange'] = res['xrange'] - res['yrange']
	res['xstd'],   res['ystd']   = np.std(betas, axis=0)

	# feature correlation
	res['correlation'] = np.corrcoef(betas, rowvar = False)[0][1]
	if np.isnan(res['correlation']):
		res['correlation'] = 0.0

	# total area of convex hull
	res['area'] = ConvexHull(jitterize(betas, sd = 0.0001)).volume

	# distances 
	within_mat = pdist(betas, betas)
	res['within'] = np.mean(within_mat[np.triu(within_mat)>0])
	if alphas is not None:
		res['between'] = np.mean(pdist(alphas, betas))
	
	return res


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


def histvec(X, bins, density = False):
	"""
	MATLAB-like histogram function, with items in vector X being placed
	into the bin with the least difference.

	if density = True, the histogram is normalized.
	"""

	D = np.atleast_2d(bins).transpose() - np.atleast_2d(np.array(X)) 
	D = np.abs(D)
	assignment = np.argmin(D, axis=0)
	counts = [np.sum(assignment==i) for i in range(len(bins))]
	counts = np.array(counts)
	if density: counts = counts / float(np.sum(counts))
	return counts


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


def softmax(X, theta = 1.0, axis = None):
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
	y = y - np.expand_dims(np.nanmax(y, axis = axis), axis)
	
	# exponentiate y, then convert nans into 0
	y = np.exp(y)
	y[np.isnan(y)] = 0.0

	# take sum along axis, divide elementwise
	ax_sum = np.expand_dims(np.sum(y, axis = axis), axis)
	p = y / ax_sum

	# flatten if X was 1D
	if len(X.shape) == 1:
		p = p.flatten()
	return p