import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
execfile('Imports.py')
import Modules.Funcs as funcs

#pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT condition,gentype,participant from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()


data = {'condition':'','gentype':0}
gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma
gentypeStrDisp = ['A\'','B','C'] #not alpha, only beta, beta

#eyeballed betagroups
betagroups = ['Rows','Columns','Clusters','Dispersed']
#Manual entry of eyeballed betagroup
manual = dict(zip(betagroups,[[] for _ in range(len(betagroups))]))
manual['Rows'] = [144,115,18,117,121,186,134,145,54,124,40,127,114,77,49,116,153,120,73,42,47,143,89,141,166,16,46,70]
manual['Columns'] = [28,58,26,64,62,33,104,147,68,177,150,180,39,78,30,82,86,151,110,69,29,20,161,101,91]
manual['Clusters'] = [55,95,59,87,148,97,23,169,149,103,185,99,93,123,19,106,85,126,25,81,74,100]
manual['Dispersed'] = [57,172,75,108,112,72,140,158,184,139,160,154,138,79,21,98,136,43,56,181,61,178,135,163,48,60,22,132,173,36,80,50,159,182,96,71,119,65,131,165,90]
total_len = 0
manual_arr = []
#Convert to array
for group in manual.keys():
    #Remove accidental duplicates
    arr_list = list(np.unique(np.array(manual[group])))    
    total_len += len(arr_list)
    for arr_el in arr_list:
        manual_arr += [[arr_el, group]]
        
#Merge into new dataframe
manual_pd = pd.DataFrame(columns=('participant','betagroup'),data = manual_arr)
info_merge = pd.merge(info.copy(),manual_pd,on='participant',how='left')

print 'Total n (Manual) = ' + str(total_len)
print 'Total n (Actual) = ' + str(len(info))
if total_len == len(info):
    print 'Cool, ns are equal.'
else:
    print 'Looks like ns are not equal.'
    #Check for where participants might not be assigned a betagroup
    print [row['participant']  for i,row in info_merge.iterrows() if type(row['betagroup']) != str]

#Build histogram

bary = [sum(info_merge.betagroup==grp) for grp in manual.keys()]
