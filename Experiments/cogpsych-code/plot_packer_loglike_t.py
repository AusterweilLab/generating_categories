import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import Packer, CopyTweak

# get trials pickle
# pickle can be "pickles/all_data_e1_e2.p", "pickles/nosofsky1986.p"
with open("pickles/all_data_e1_e2.p", "rb" ) as f:
	trials = pickle.load( f )

# get best params pickle
# pickle can be "pickles/best_params_all_data_e1_e2.p", "pickles/best_params_nosofsky1986.p"
with open("pickles/best_params_all_data_e1_e2.p", "rb" ) as f:
	best_params = pickle.load( f )

# compute copytweak loglike
start_params = best_params[CopyTweak.model]

# set up grid of param values
gamma_grid = np.linspace(0, 1.50, 100)
loglikes = np.empty(gamma_grid.shape)

# add task type to trials object
trials.task = 'generate'

# evaluate loglike at each grid point
for i, val in enumerate(gamma_grid):
	curr = start_params.copy()
	curr['tradeoff'] = val
        curr = Packer.parmxform(curr, direction = 1)
	loglikes[i] = -trials.loglike(curr, Packer)


for i in range(len(gamma_grid)):
	print i, gamma_grid[i], loglikes[i]

# plot it
fh = plt.figure(figsize=(5,3))

# copytweak annotation
copytweak_loglike = loglikes[gamma_grid == 0]
plt.plot([min(gamma_grid), max(gamma_grid)], [copytweak_loglike, copytweak_loglike], '--', linewidth = 1, color='gray')
plt.text(0.5, copytweak_loglike, 'Target Only (Copy \& Tweak)', ha = 'center', va = 'bottom')

# contrast only annotation
contrast_loglike = loglikes[gamma_grid == 2]
#plt.plot([min(gamma_grid), max(gamma_grid)], [contrast_loglike, contrast_loglike], '--', linewidth = 1, color='gray')
#plt.text(0.5, contrast_loglike, 'Contrast Only', ha = 'center', va = 'bottom')

# PACKER annotation
x = float(gamma_grid[loglikes == max(loglikes)])
plt.text(x, max(loglikes) + 5, 'PACKER', ha = 'center', va = 'bottom', fontsize = 12)


# plot main line
plt.plot(gamma_grid, loglikes,'k-', linewidth = 1)
plt.xlabel('$\gamma$ Parameter Value', fontsize = 12)

xticks = np.arange(min(gamma_grid),max(gamma_grid)+0.2,0.2)
xticklabels = [str(i) for i in xticks]
xticklabels[0] = '0'
xticklabels[-1] = '1'
#plt.xticks(xticks)
fh.gca().set_xticklabels(xticklabels)

yticks = np.arange(-4950,-4650,50)
yticklabels = [str(i) for i in yticks]
plt.yticks(yticks)
fh.gca().set_yticklabels(yticklabels)

plt.gca().yaxis.grid(True)
plt.ylabel('Log-Likelihood ($L$)', fontsize = 12)

plt.savefig('packer-loglike-t.png', bbox_inches='tight', transparent=False)
#path = '../../Manuscripts/cog-psych/figs/packer-loglike-t.pgf'
#funcs.save_as_pgf(fh, path)
