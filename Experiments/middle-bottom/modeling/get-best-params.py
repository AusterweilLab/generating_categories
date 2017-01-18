import sys, pickle
import pandas as pd
import numpy as np

import scipy.optimize as op

# add modeling module
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
from models import CopyTweak, Packer, ConjugateJK13, Optimize
import utils

# get data from pickle
with open( "data.pickle", "rb" ) as f:
	trials, stimuli = pickle.load( f )


# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 

for o in [CopyTweak, Packer, ConjugateJK13]:
	inits = np.random.uniform(low = 1.0001, high = 2.0, size = (4,)).tolist()

	# edit for model specific ranges
	if o == CopyTweak:
		inits[1] = inits[1] - 1.5 # within pref could be positive or negative
		inits[2] = inits[2] - 1.0 # tolerance is [0 1]

	if o == ConjugateJK13:
		inits[0] = inits[0] - 1.0 # categiry mean bias should be smallish
		inits[2] = inits[2] - 1.0 # domain variance assumption should be smallish

	Optimize.hillclimber(o, inits, trials, stimuli, options)