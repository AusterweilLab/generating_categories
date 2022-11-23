import numpy as np


def dummycode_colors(X, hues = None):
	"""
		function to convert hue value into a color category
	"""
	# naturalish categorization via https://en.wikipedia.org/wiki/File:HueScale.svg
	if hues is None:

		# # naturalish categorization via https://en.wikipedia.org/wiki/File:HueScale.svg
		# hues = np.array([[0,60,120,180,240,300,360]]).T / 360.0

		# # Intermediates
		# hues = np.array([[0,30,60,90,120,150,180,210,240,270,300,330,360]]).T / 360.0
		hues = np.array([[0, 45, 90, 135, 180, 225, 270, 315, 360]]).T / 360.0

		# # 0.15s used by jk13, with added 1.0 at end
		# hues = np.array([[ 0,54,108,162,216,270,324, 360]]).T / 360.0

	k = len(hues)
	D = np.abs(hues - np.atleast_2d(np.array(X)))
	assignment = np.argmin(D, axis=0)
	assignment[assignment==(k-1)] = 0
	return assignment