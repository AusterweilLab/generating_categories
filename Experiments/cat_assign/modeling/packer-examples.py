import matplotlib.pyplot as plt
import numpy as np
from itertools import product

execfile('Imports.py')
from Modules.Classes import Packer
import Modules.Funcs as funcs


vals = np.linspace(-1, 1, 200).tolist()
space = np.fliplr(funcs.cartesian([vals, vals]))

A = np.array([[-0.25, -0.25]])
B = np.array([[ 0.25,  0.25]])
cats = [A,B]

# params for PACKER
c, theta = 1.0, 3.

pos =     [c, 1.0, theta]
neg =     [c, 0.0, theta]
pos_neg = [c, 0.5, theta]

prob_spaces = {
    'Target Influence': Packer(cats,pos),
    'Contrast Influence': Packer(cats,neg),
    'Combination': Packer(cats,pos_neg)
}

f, ax = plt.subplots(1,3, figsize = (7.5, 1.5))

prefix = ['(a)','(b)','(c)']
for i, k in enumerate(['Contrast Influence', 'Target Influence', 'Combination']):
    m = prob_spaces[k] 
    h = ax[i]

    ps = m.get_generation_ps(space,1)
    print max(ps)

    g = funcs.gradientroll(ps, 'roll')[:,:,0]
    im = funcs.plotgradient(h, g, A, B, cmap = 'Blues', beta_col = 'w')

    title = prefix[i] + ' ' + k
    h.set_title(title, fontsize = 11)

    tradeoffstr = str(m.tradeoff)
    if tradeoffstr in ['0.0', '1.0']:
        tradeoffstr = tradeoffstr[0]
    xlab  = '$\{'
    xlab += 'c = ' + str(int(c)) + ','
    xlab += '\gamma = ' + tradeoffstr  + ','
    xlab += '\\theta = ' + str(int(theta))
    xlab += '\}$'
    h.set_xlabel(xlab)


# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.16, 0.03, 0.66])
f.colorbar(im, cax=cbar, ticks = [0, np.max(g)])
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)


f.savefig('packer-examples.pdf', bbox_inches='tight', transparent=True)

# path = '../../../Manuscripts/cogsci-2017/figs/packer-examples.pgf'
# funcs.save_as_pgf(f, path)
