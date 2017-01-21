import numpy as np
import utils

def plotclasses(h, stimuli, alphas, betas):
	textsettings = dict(
		verticalalignment='center', 
		horizontalalignment='center',
		fontsize = 11.0)

	h.axis(np.array([-1, 1, -1, 1])*1.2)
	for i in alphas:
		x, y = stimuli[i,0], stimuli[i,1]
		h.text(x,y,'A',color = 'r', **textsettings)

	for i in betas:
		x, y = stimuli[i,0], stimuli[i,1]
		h.text(x,y,'B',color = 'b', **textsettings)

	h.set_yticks([])
	h.set_xticks([])
	h.set_aspect('equal', adjustable='box')


def plotgradient(h, G, alphas, betas, 
								clim = (), 
								cmap = 'Blues',
								alpha_col = 'red',
								beta_col = 'black',
								):
	"""
	Plot a gradient using matplotlib.
	 - h is the handle to the axis
	 - G is the matrix being plotted, 
	 - alphas/betas are the [-1 +1] coordinates of category memebers
	 - clim (optional) defines the limits of the colormap.
	 - cmap (optional) deinfes the colormap
	 - [alpha/beta]_col: color of alpha and beta markers
	"""

	# generate clims if not provided
	if not clim:
		clim = (0, np.max(G))

	# make sure G is 2D
	if G.ndim > 2:
		raise Exception("G has too many dimensions. Size: " + str(G.shape))

	# plot gradient
	im = h.imshow(np.flipud(G), 
		clim = clim, 
		origin='lower', 
		interpolation="nearest", 
		cmap = cmap
	)

	# show annotations
	textsettings = dict(va = 'center', ha = 'center', fontsize = 12.0)

	coords = gradientspace(alphas, G.shape[0])
	for j in range(coords.shape[0]):
		h.text(coords[j,0],coords[j,1], 'A',
			color = alpha_col, **textsettings)

	coords = gradientspace(betas, G.shape[0])
	for j in range(coords.shape[0]):
		h.text(coords[j,0],coords[j,1], 'B',
			color = beta_col, **textsettings)

	h.set_yticks([])
	h.set_xticks([])
	h.set_aspect('equal', adjustable='box')
	h.axis([-0.5, G.shape[1]-0.5, -0.5, G.shape[0]-0.5])
	return im
	
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

