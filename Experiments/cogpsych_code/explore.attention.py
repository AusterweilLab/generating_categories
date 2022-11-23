import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import pandas as pd


execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13, Optimize
import Modules.Funcs as funcs

pd.set_option('precision', 3)
np.set_printoptions(precision = 3)

 # 72 73 74 75 76 77 78 79 80
 # 63 64 65 66 67 68 69 70 71
 # 54 55 56 57 58 59 60 61 62
 # 45 46 47 48 49 50 51 52 53
 # 36 37 38 39 40 41 42 43 44
 # 27 28 29 30 31 32 33 34 35
 # 18 19 20 21 22 23 24 25 26
 #  9 10 11 12 13 14 15 16 17
 #  0  1  2  3  4  5  6  7  8
vals = np.linspace(-1, 1, 9).tolist()
stimuli = np.fliplr(np.array(list(product(vals, vals))))


alphas =  [30, 32, 48, 50]
alphas =  [12, 30, 14, 32]
betas = []

models = [ # these values copied on Jan 29!
    [CopyTweak, dict(
    specificity = 4.67536899146,
    tolerance = 0.895345369763,
    determinism = 5.60105216678,
        )],
    [Packer, dict(
    specificity = 0.565028848775,
    between = -4.81445541313,
    within = 4.2500267818,
    determinism = 0.731417901569,
        )],
    [ConjugateJK13, dict(
    category_mean_bias = 1e-10,
    category_variance_bias = 1.00000753396,
    domain_variance_bias = 1.21974609442,
    determinism = 7.14705600068,
        )],
]

wt_list = [[0.5, 0.5], [0.15, 0.85],[0.85,0.15]]
FUN, PARAMS = models[0]

f, ax = plt.subplots(1, 3, figsize = (6.5, 2))
pltnum = 0
for wts in wt_list:
    A = stimuli[alphas,:]
    B = stimuli[betas,:]
    PARAMS['wts'] = wts

    M = FUN([A, B], PARAMS) 
    print M
    simulated_betas = M.simulate_generation(stimuli, 1, nexemplars = 3)
    simulated_B = stimuli[simulated_betas,:]
    ps = M.get_generation_ps(stimuli, 1)

    g = funcs.gradientroll(ps,'roll')[:,:,0]
    h = ax[pltnum]
    funcs.plotgradient(h, g, A, simulated_B, clim = (0, 0.15))

    h.set_title(str(wts), fontsize = 10)
    if wts == wt_list[0]:
        h.set_ylabel(FUN.model)
    pltnum += 1

f.savefig('explore.attention.png', bbox_inches='tight', transparent=False)
