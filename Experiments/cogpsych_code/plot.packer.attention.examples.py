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
params = dict(
    specificity = 1.0,
    theta_cntrst = 1.5, #0.5
    theta_target = 1.5
)

wts = dict(
    X = np.array([0.7,0.3]),
    Y = np.array([0.3,0.7]),
    Even = np.array([0.5,0.5])
)

f, ax = plt.subplots(1,3, figsize = (7.5, 2.))

prefix = ['(a)','(b)','(c)']
for i, k in enumerate(['X','Y','Even']):
    params['wts'] = wts[k] 
    m = Packer(cats,params)

    h = ax[i]

    ps = m.get_generation_ps(space,1)
    print max(ps)

    g = funcs.gradientroll(ps, 'roll')[:,:,0]
    im = funcs.plotgradient(h, g, A, B, cmap = 'Blues', beta_col = 'w')

    title = prefix[i]
    h.set_title(title, fontsize = 11)

    wtstr = '$\{'
    wtstr += 'w_1=' + str(wts[k][0])
    wtstr += ', '
    wtstr += 'w_2=' + str(wts[k][1])
    wtstr += '\}$'
    h.set_xlabel(wtstr)


# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.16, 0.03, 0.66])
f.colorbar(im, cax=cbar, ticks = [0, np.max(g)])
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)


f.savefig('packer-attention-examples.png', bbox_inches='tight', transparent=False)

path = '../../Manuscripts/cog-psych/revision/figs/packer-attention-examples.pgf'
funcs.save_as_pgf(f, path)
