import pickle, math
import pandas as pd
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs
from Modules.Classes import Simulation
from Modules.Classes import CopyTweak
from Modules.Classes import Packer
from Modules.Classes import ConjugateJK13
from Modules.Classes import RepresentJK13
from scipy.stats import stats as ss
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

#Get learning data
data_assign_file = '../cat-assign/data/experiment.db'
con = sqlite3.connect(data_assign_file)
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * FROM assignment", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()


bestparmdb = "pickles/chtc_gs_best_params_corr.p"
with open(bestparmdb, "rb" ) as f:
    best_params_t = pickle.load( f )

#Rebuild it into a smaller dict
best_params = dict()
for modelname in best_params_t.keys():    
    best_params[modelname] = dict()
    for i,parmname in enumerate(best_params_t[modelname]['parmnames']):
        parmval = best_params_t[modelname]['bestparmsll']
        best_params[modelname][parmname] = parmval[i]

model_obj = Packer
modelname = model_obj.model

categories = [eval(info.stimuli[0])[0:4],eval(info.stimuli[0])[4:8]]

params = best_params[modelname]
with open('pickles/private/corrprepvar.p','rb') as f:
    prepvar = pickle.load(f)

pptdata = prepvar[0]
tso = prepvar[1]
try:
    funcs.get_corr(params,pptdata,tso,model_obj)
except:
    #Let's just look at the first ppt in info for now
    paramst = model_obj.parmxform(params,direction=1)
    Simulation.loglike_allperm(params,model_obj,categories,stimuli,permute_category=1)
