import matplotlib.pyplot as plt
import numpy as np
from itertools import product

import sys
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

vals = np.linspace(-1, 1, 100).tolist()
space = np.fliplr(utils.cartesian([vals, vals]))

A = np.array([[-0.25, -0.25]])
B = np.array([[ 0.25,  0.25]])

def getss(examples, space, direction, c = 2.0):
    D = utils.pdist(space, examples)
    S = np.exp(-1.0 * float(c) * D)
    S *= direction
    return np.sum(S, axis=1)

neg = getss(A, space, -1.0) * 1.0
pos = getss(B, space, 1.0) * 0.5


prob_spaces = {
    'Target Influence': pos,
    'Contrast Influence': neg,
    'Combination': pos + neg
}

f, ax = plt.subplots(1,3, figsize = (7, 2.5))
counter = 0

for k in ['Contrast Influence', 'Target Influence', 'Combination']:
    v = prob_spaces[k] 
    h = ax[counter]

    ps = np.exp(v * 3.0)
    ps = ps / float(sum(ps))
    print max(ps)
    g = utils.gradientroll(ps, 'roll')[:,:,0]
    im = utils.plotgradient(h, g, A, B, clim = (0, 0.00025), cmap = 'Blues')
    h.set_title(k, fontsize = 11)

    counter += 1

f.savefig('example-prob-spaces.png', bbox_inches='tight', transparent=False)

import os, matplotlib
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'
opts = {'pgf.texsystem': 'pdflatex'}
matplotlib.rcParams.update(opts)
f.savefig('../../../Manuscripts/cogsci-2017/figs/example-prob-spaces.pgf', bbox_inches='tight')
