# some plotting helpers
from util.funcs import *


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

	h.get_xaxis().set_visible(False)
	h.get_yaxis().set_visible(False)
	h.set_aspect('equal', adjustable='box')


def plotgradient(h, G, alphas, stimuli, clim = (), cmap = 'Blues'):
	"""
	Plot a gradient using matplotlib.
	 - h is the handle to the axis
	 - G is the matrix being plotted, 
	 - alphas are the known members of the alpha category
	 - clim (optional) defines the limits of the colormap.
	"""

	# generate clims if not provided
	if not clim:
		clim = (np.min(G), np.max(G))

	# make sure G is 2D
	if G.ndim > 2:
		raise Exception("G has too many dimensions. Size: " + str(G.shape))

	# plot gradient
	h.imshow(np.flipud(G), clim = clim, 
		origin='lower', interpolation="nearest", cmap = cmap)

	# rescale stimulus coordinates
	scstimuli = gradientspace(stimuli, G.shape[0])

	# show annotations
	textsettings = dict(
		verticalalignment='center', 
		horizontalalignment='center',
		fontsize = 11.0)

	coords = scstimuli[alphas,:]
	for j in range(coords.shape[0]):
		h.text(coords[j,0],coords[j,1], 'A',
			color = 'red', **textsettings)

	h.get_xaxis().set_visible(False)
	h.get_yaxis().set_visible(False)
	h.set_aspect('equal', adjustable='box')
	h.axis([-0.5, G.shape[1]-0.5, -0.5, G.shape[0]-0.5])