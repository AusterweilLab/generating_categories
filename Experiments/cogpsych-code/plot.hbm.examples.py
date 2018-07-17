import matplotlib.pyplot as plt
import numpy as np
from itertools import product

execfile('Imports.py')
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
import Modules.Funcs as funcs


vals = np.linspace(-1, 1, 200).tolist()
space = np.fliplr(funcs.cartesian([vals, vals]))

# A = np.array([[-0.25, -0.25],[-0.50, -0.25],[-0.50, -0.50],[ -0.25, -0.50]])
# B = np.array([[ 0.25,  0.25],[ 0.50,  0.25],[ 0.50,  0.50],[  0.25,  0.50]])
A = np.array([[-0.50, -0.50]])
B = np.array([[ 0.50,  0.50]])

cats = [A,B]

# params
kappa, nu, lda, theta = 0, 1, 1, 3

# pos =     [c, 0.0, theta] #target similarity only
# neg =     [c, theta, 0.0] #contrast similarity only
# pos_neg = [c, theta, theta] #both contrast and target
parms = [kappa, nu, lda, theta]
prob_spaces = {
    'Hierarchical Bayes': ConjugateJK13(cats,parms),
    'Representativeness': RepresentJK13(cats,parms),
}

f, ax = plt.subplots(1,2, figsize = (5, 2.))

prefix = ['(a)','(b)']
for i, k in enumerate(['Hierarchical Bayes', 'Representativeness']):
    m = prob_spaces[k] 
    h = ax[i]

    ps = m.get_generation_ps(space,1)
    print ps.max()

    g = funcs.gradientroll(ps, 'roll')[:,:,0]
    im = funcs.plotgradient(h, g, A, B, cmap = 'Blues', beta_col = '#21e521')

    title = prefix[i] + ' ' + k
    h.set_title(title, fontsize = 11)

    #if tradeoffstr in ['0.0', '10.0']:
    #    tradeoffstr = tradeoffstr[0]
    # xlab  = '$\{'
    # xlab += '\\kappa = ' + str(int(kappa)) + ','
    # xlab += '\\nu = ' + str(int(nu))  + ','
    # xlab += '\\lambda = ' + str(int(lda)) + ','
    # xlab += '\\theta = ' + str(int(theta))
    # xlab += '\}$'
    # xlab = k
    #h.set_xlabel(xlab)


# add colorbar
f.subplots_adjust(right=0.8)
cbar = f.add_axes([0.83, 0.16, 0.03, 0.66])
f.colorbar(im, cax=cbar, ticks = [0, np.max(g)])
cbar.set_yticklabels(['Lowest\nProbability', 'Greatest\nProbability'])
cbar.tick_params(length = 0)


fname = 'hbm-examples'
f.savefig('hbm-examples.pdf', bbox_inches='tight', transparent=True)

path = '../../Manuscripts/cog-psych/revision/figs/hbm-examples.pgf'
funcs.save_as_pgf(f, path)
