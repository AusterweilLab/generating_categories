#analyse some statistics to see if participants show regularity
# That is, whether they tend to generate novel categories that are of the same hue
import pickle
import pandas as pd
import scipy.stats
import sqlite3
import os,sys

os.chdir(sys.path[0])
exec(open('Imports.py').read())

#TODO: import of local files in JK13 needs to be fixed 
import Modules.Funcs as funcs
from JK13 import JK13, JKFuncs
import numpy as np

#First, show the average distance between
con = sqlite3.connect('experiment.db')
distances = pd.read_sql_query("SELECT * from distances", con)
training = pd.read_sql_query("SELECT * from training", con)
generation = pd.read_sql_query("SELECT * from generation", con)
con.close()

# set hue categories
# hues = np.array([[0,30,60,90,120,150,180,210,240,270,300,330,360]]).T / 360.0
hues = np.array([[0, 45, 90, 135, 180, 225, 270, 315, 360]]).T / 360.0

# get number of distinct items for each participant
shared_hues = dict( (i,np.array([])) for i in JK13.conditions)
checkregularity = []
mode_prop = []
for (i, c), rows in generation.groupby(['participant','condition']):
    idx = (training.participant == i) & (training.condition == c)
    As = JKFuncs.dummycode_colors(training.loc[idx].Hue.as_matrix(), hues=hues)
    Bs = JKFuncs.dummycode_colors(rows.Hue.as_matrix(), hues=hues)
    nBs = float(len(Bs))
    if all(Bs[0]==Bs):
        checkregularity += [True]        
    else:
        checkregularity += [False]
        
    mode_prop += [scipy.stats.mode(Bs)[1]/nBs]
    
    # num_distinct = np.sum(np.in1d(Bs,As)==1)
    # shared_hues[c] = np.append(shared_hues[c],num_distinct)

regularity_prop = sum(checkregularity)/float(len(checkregularity))
mode_mean = sum(mode_prop)/len(mode_prop)

print('Total number of generated categories: {}'.format(len(mode_prop)))
print('Generated categories with complete regularity (all exemplars of same hue): {}({})'.format(sum(checkregularity),regularity_prop))
print('Mean regularity (mean proportion of category with modal hue): {}'.format(mode_mean[0]))
print('Mean distance between trained and generated category: {}'.format(distances.Between.mean()))
print('Mean distance within generated category: {}'.format(distances.Within.mean()))
