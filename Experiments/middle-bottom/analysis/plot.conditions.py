import sqlite3, os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils



# 72 73 74 75 76 77 78 79 80
# 63 64 65 66 67 68 69 70 71
# 54 55 56 57 58 59 60 61 62
# 45 46 47 48 49 50 51 52 53
# 36 37 38 39 40 41 42 43 44
# 27 28 29 30 31 32 33 34 35
# 18 19 20 21 22 23 24 25 26
#  9 10 11 12 13 14 15 16 17
#  0  1  2  3  4  5  6  7  8
values = np.linspace(-1, 1, 9)
alphas = dict(
	Middle = [30, 32, 48, 50 ],
	Bottom = [12, 14, 30, 32],
)

stimuli = np.fliplr(utils.cartesian([values, values]))
textsettings = dict(
		verticalalignment='top', 
		horizontalalignment='left',
		fontsize = 11.0)



f, ax= plt.subplots(1,2, figsize=(3, 1.5))
counter = 0
for k, a  in alphas.items():
	h = ax[counter]
	utils.plotclasses(h, stimuli, a, [])		
	h.set_title(k)
	h.axis([-1.2, 1.2, -1.2, 1.2])
	[i.set_linewidth(0.75) for i in h.spines.itervalues()]

	counter += 1
# plt.show()
f.savefig('conditions.png', bbox_inches='tight', transparent=False)


import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
f.savefig('../../../Manuscripts/cogsci-2017/figs/middle-bottom-conditions.pgf',
	bbox_inches='tight', transparent=False)