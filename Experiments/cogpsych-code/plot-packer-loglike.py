import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import Packer

# get trials pickle
# get data from pickle
with open("pickles/all_data_e1_e2.p", "rb" ) as f:
	trials = pickle.load( f )


# best fit from PACKER
start_params = dict(
	specificity =  0.481287831406, 
	between 		= -0.945026920024, 
	within			=  1.0440682555, 
	determinism	=  3.35432164741
)

# best fit from copytweak
start_params = dict(
	specificity =  3.18895961945, 
	between 		=  0.0, 
	within			=  1.0, 
	determinism	=  2.96847856016
)

# copytweak loglike
copytweak = -4919.17291327

between_grid = np.linspace(-1.6, 0, 100)

loglikes = np.empty(between_grid.shape)
for i, val in enumerate(between_grid):
	curr = start_params.copy()
	curr['between'] = val
	loglikes[i] = -trials.loglike(curr, Packer)


# plot it
fh = plt.figure(figsize=(5,3))
plt.plot([min(between_grid), max(between_grid)],[copytweak,copytweak], '--', linewidth = 1, color='gray')
plt.text(-0.8, copytweak, 'Copy \& Tweak', ha = 'center', va = 'bottom')

plt.plot(between_grid, loglikes,'k-', linewidth = 1)
plt.text(-1.0, -4735, 'PACKER', ha = 'right', va = 'bottom')


plt.xlabel('$\phi$ Parameter Value')
plt.xticks(np.arange(min(between_grid),max(between_grid)+0.2,0.2))
plt.gca().yaxis.grid(True)
plt.ylabel('Log-Likelihood ($L$)')

plt.savefig('packer-loglike.png', bbox_inches='tight', transparent=False)
path = '../../Manuscripts/cog-psych/figs/packer-loglike.pgf'
funcs.save_as_pgf(fh, path)
