import pickle
import pandas as pd

execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13

# get trials pickle
# get data from pickle
with open("pickles/all_data_e1_e2.p", "rb" ) as f:
	trials = pickle.load( f )

# options for the optimization routine
options = dict(
	method = 'Nelder-Mead',
	options = dict(maxiter = 500, disp = False),
	tol = 0.01,
) 

for model_obj in [Packer, CopyTweak, ConjugateJK13]:

	res = Simulation.hillclimber(model_obj, trials, options)