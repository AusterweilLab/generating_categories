import numpy as np


def dummycode_colors(X):
	"""
		function to convert hue value into a color category
	"""

	# naturalish categorization via https://en.wikipedia.org/wiki/File:HueScale.svg
	hue_categories = np.array([[0,60,120,180,240,300,360]]).T / 360.0

	# 0.15s used by jk13, with added 1.0 at end
	# hue_categories = np.array([[ 0,54,108,162,216,270,324, 360]]).T / 360.0

	k = len(hue_categories)
	D = np.abs(hue_categories - np.atleast_2d(np.array(X)))
	assignment = np.argmin(D, axis=0)
	assignment[assignment==(k-1)] = 0
	return assignment