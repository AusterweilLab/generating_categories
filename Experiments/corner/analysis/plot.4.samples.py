import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys

os.chdir(sys.path[0])

exec(open('Imports.py').read())
import Modules.Funcs as funcs

#TODO: BREAKS ON CLUSTER!?
#       NO CLUSTER IN ALPHAS -- JUST CORNER_S CORNER_C


con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()
con.close()

profiles = ['Row','Column','Cluster','Dispersed','Positive','Negative',]
samples = dict(
    Cluster = [
        199, #Row
        248, #Column
        254, #Cluster
        229, #Dispersed
        305, #Positive
        152, #Negative
        ]
    # Row = [
    #     11, # 4 corner
    #     91, # top row / corners
    #     106, # side column
    #     117, # top cluster
    # ]
    # XOR = [
    #     11, # 4 corner
    #     91, # top row / corners
    #     106, # side column
    #     117, # top cluster
    # ]
)

fh, ax = plt.subplots(2,3, figsize = [4, 3])#plt.subplots(2,4, figsize = [3.2, 1.6])
#fh, ax = plt.subplots(1,6, figsize = [8, 4])#plt.subplots(2,4, figsize = [3.2, 1.6])
#fh, ax = plt.subplots(1,8, figsize = [8.1, 1])

ax = ax.flat
plotnum = 0
for k, v in samples.items():
    for pid in v:
        h = ax[plotnum]

        A = alphas[k]
        B = generation.loc[generation.participant == pid, 'stimulus']
        funcs.plotclasses(h, stimuli, A, B, textsettings = dict(fontsize = 12))
        h.set_title(profiles[plotnum])
        plotnum += 1
         

plt.tight_layout(pad=-0.0, w_pad=-0.0)
fh.savefig('beta.samples.pdf', bbox_inches = 'tight', transparent = True)
#fh.savefig('beta.samples.png', bbox_inches = 'tight', transparent = True)

# path = '../../../Manuscripts/cogsci-2017/figs/beta.samples.pgf'
# funcs.save_as_pgf(f, path)

