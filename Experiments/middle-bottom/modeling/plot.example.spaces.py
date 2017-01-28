import matplotlib.pyplot as plt
import numpy as np
from itertools import product

execfile('Imports.py')
from Modules.Classes import Packer
import Modules.Funcs as funcs

vals = np.linspace(-1, 1, 100).tolist()
space = np.fliplr(funcs.cartesian([vals, vals]))

A = np.array([[-0.25, -0.25]])
B = np.array([[ 0.25,  0.25]])
cats = [A,B]

# params for PACKER
c, phi = 1.0, 3.0

pos =     [c,  0.0, 1.0, phi]
neg =     [c, -1.0, 0.0, phi]
pos_neg = [c, -1.0, 1.0, phi]

prob_spaces = {
    'Target Influence': Packer(cats,pos),
    'Contrast Influence': Packer(cats,neg),
    'Combination': Packer(cats,pos_neg)
}

f, ax = plt.subplots(1,3, figsize = (7.5, 2.5))
counter = 0

for k in ['Contrast Influence', 'Target Influence', 'Combination']:
    m = prob_spaces[k] 
    h = ax[counter]

    ps = m.get_generation_ps(space,1)
    print max(ps)

    g = funcs.gradientroll(ps, 'roll')[:,:,0]
    im = funcs.plotgradient(h, g, A, B, cmap = 'Blues', beta_col = 'w')
    h.set_title(k, fontsize = 11)

    counter += 1


# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.225, 0.03, 0.54])
f.colorbar(im, cax=cbar, ticks = [0,0.000276585446215])
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)

f.savefig('example-prob-spaces.png', bbox_inches='tight', transparent=False)

path = '../../../Manuscripts/cogsci-2017/figs/example-prob-spaces.pgf'
# funcs.save_as_pgf(f, path)
