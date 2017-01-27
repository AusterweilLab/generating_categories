import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import pandas as pd


execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13
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
betas = [0, 9]

models = [
    [CopyTweak, dict(
        specificity = 9.4486327043,
        within_pref = 17.0316650379,
        tolerance = 0.403108523886,
        determinism = 7.07038770338,
        )],
    [Packer, dict(
        specificity = 0.562922970884,
        between = -1.76500997943,
        within = 1.55628620461,
        determinism = 1.99990124401,
        )],
    [ConjugateJK13, dict(
        category_mean_bias = 0.0167065365661,
        category_variance_bias = 1.00003245067,
        domain_variance_bias = 0.163495499745,
        determinism = 30.10276377982,
        )],
]


f, ax = plt.subplots(1, 3, figsize = (6.5, 2))
pltnum = 0
for FUN, params in models:
    A = stimuli[alphas,:]
    B = stimuli[betas,:]
    
    M = FUN([A, B], params) 
    ps = M.get_generation_ps(stimuli, 1)

    g = funcs.gradientroll(ps,'roll')[:,:,0]
    h = ax[pltnum]
    funcs.plotgradient(h, g, A, B, clim = (0, 0.15))
    h.set_title(FUN.model, fontsize = 12)
    pltnum += 1

f.savefig('model-comparison.png', bbox_inches='tight', transparent=False)
