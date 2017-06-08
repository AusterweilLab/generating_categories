import numpy as np
import pandas as pd
pd.set_option('precision', 3)
np.set_printoptions(precision = 3)

import pickle

# custom modules
execfile('Imports.py')
from Modules.Classes import CopyTweak, Packer, ConjugateJK13
import Modules.Funcs as funcs

models = [CopyTweak, Packer, ConjugateJK13]


# define pickle files --  all data
parampickle = "pickles/best_params_all_data_e1_e2.p"
responsepickle = "pickles/all_data_e1_e2.p"

# # define pickle files --  exclude first trial
# parampickle = "pickles/best_params_trials_2-4_e1_e2.p"
# responsepickle = "pickles/trials_2-4_e1_e2.p"

# get best params pickle
with open(parampickle, "rb" ) as f:
    best_params = pickle.load( f )

# get dataset pickle
with open(responsepickle, "rb" ) as f:
    responseset = pickle.load( f )

n = responseset.nresponses

for m in models:
    modelname = m.model
    k = len(m.parameter_names)
    params = best_params[modelname]

    L = -1. * responseset.loglike(params, m)
    AIC = 2.*k - 2.*L
    AICc = AIC + ((2.*k * (k+1)) / (n + k + 1.))
    BIC = np.log(n)*k - 2.*L

    S = modelname + '\n'
    for k, v in [('L',L),('AIC',AIC),('AICc',AICc),('BIC',BIC)]:
        S += k + ' = ' + str(round(v,2)) + '\n'
    print S

# likelihood ratio test
from scipy.stats import chisqprob
l1 = -1. * responseset.loglike(best_params[CopyTweak.model], CopyTweak)
l2 = -1. * responseset.loglike(best_params[Packer.model], Packer)
D = 2.* (l2 - l1)
print 'Likelihood Test for Packer vs. CopyTweak'
print 'D = ' + str(round(D,2))
print 'df = ' + str(1)
print 'p = ' + str(round(chisqprob(D,1),2))

