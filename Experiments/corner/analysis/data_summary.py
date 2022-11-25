import sqlite3, os, sys
import numpy as np
import pandas as pd

os.chdir(sys.path[0])


exec(open('Imports.py').read())
import Modules.Funcs as funcs

pd.set_option('display.precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()

con.close()

savedir = 'individuals'
gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma
gentypeStrDisp = ['A\'','B','C'] #not alpha, only beta, beta-gamma
gentypeStrLong = ['Not-Alpha-Only','Beta-Only     ', 'Beta-Gamma    ']
for condition, rows in info.groupby('condition'):
    for gentype, rowss in rows.groupby('gentype'):
        print(condition, gentypeStrLong[gentype], 'n =', len(rowss))

print('Total N = {}'.format(len(info)))
