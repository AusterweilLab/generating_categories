import sqlite3, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

execfile('Imports.py')
import Modules.Funcs as funcs

pd.set_option('precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()

con.close()

savedir = 'individuals'
gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma
gentypeStrDisp = ['A\'','B','C'] #not alpha, only beta, beta-gamma
gentypeCols = [[.3,0,.5],[0,0,.5],[0,.5,0]]
f, ax= plt.subplots(1,1, figsize=(1.6, 1.6))
for i, row in info.iterrows():
    pid, condition, gentype = int(row.participant), row.condition, row.gentype
    gentypeStr_p = gentypeStr[gentype]

    palphas = alphas[condition]    
    pbetas = df.stimulus[df.participant == pid]
    if gentype==2:
        pdf = df.loc[df.participant==pid]
        betastr = [gentypeStrDisp[1] if pdf_row.category=='Beta' else gentypeStrDisp[2] for ii,pdf_row in pdf.iterrows() ]
        betacol = [gentypeCols[1] if pdf_row.category=='Beta' else gentypeCols[2] for ii,pdf_row in pdf.iterrows() ]
    else:
        betastr = gentypeStrDisp[gentype]
        betacol = gentypeCols[gentype]
    funcs.plotclasses(ax, stimuli, palphas, pbetas, betastr=betastr,betacol = betacol)
    
    fname = os.path.join(savedir,condition + '-' + gentypeStr_p + '-' + str(pid) + '.png')
    ax.text(.9,1.25,str(pid))
    f.savefig(fname, bbox_inches='tight', transparent=False)
    plt.cla()

