import sqlite3, os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

os.chdir(sys.path[0])


exec(open('Imports.py').read())
import Modules.Funcs as funcs

savefig = False

pd.set_option('display.precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).values
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

savedir = 'individuals'
gentypeStr = ['N','B','C'] #not alpha, only beta, beta-gamma
gentypeStrDisp = ['A\'','B','C'] #not alpha, only beta, beta-gamma
gentypeCols = [[.3,0,.5],[0,0,.5],[0,.5,0]]
if savefig:
    f, ax= plt.subplots(1,1, figsize=(1.6, 1.6))

var_thresh = .25
cor_thresh = .7
groupcount = {'Positive':0,'Negative':0,'Cluster':0,'Dispersed':0,'Row':0,'Column':0}
data_arr = []
for i, row in info.iterrows():
    pid, condition, gentype = int(row.participant), row.condition, row.gentype
    gentypeStr_p = gentypeStr[gentype]

    palphas = alphas[condition]
    pbetas_all = df.stimulus[df.participant == pid]
    if gentype==2:
        pdf = df.loc[df.participant==pid]
        betastr = [gentypeStrDisp[1] if pdf_row.category=='Beta' else gentypeStrDisp[2] for ii,pdf_row in pdf.iterrows() ]
        betacol = [gentypeCols[1] if pdf_row.category=='Beta' else gentypeCols[2] for ii,pdf_row in pdf.iterrows() ]
        pbetas_list = [pdf.stimulus[pdf.category=='Beta']]
        pbetas_list += [pdf.stimulus[pdf.category=='Gamma']]
    else:
        pbetas_list = [df.stimulus[df.participant == pid]]
        betastr = gentypeStrDisp[gentype]
        betacol = gentypeCols[gentype]
    #Add thresholds for classifying category shapes
    #get covariance matrix
    printstr = ''
    for ii,pbetas in enumerate(pbetas_list):
        covmat = np.cov(stimuli[pbetas].T)
        varx = covmat[0,0]
        vary = covmat[1,1]
        cov  = stats.correlation[stats.participant==pid].values[0]
        group = ''

        if varx > vary*5:
            group = 'Row'
        elif vary > varx*5:
            group = 'Column'
        elif cov > cor_thresh:
            group = 'Positive'
        elif cov < -cor_thresh:
            group = 'Negative'
        elif varx <= var_thresh and vary <= var_thresh:            
            group = 'Cluster'
        else:#elif varx > var_thresh and vary > var_thresh:
            group = 'Dispersed'
        # else:
        #     group = 'Irregular'
        print('{} {} {} {} {} {}'.format(pid,gentypeStr[ii+1], varx, vary, cov, group))
        printstr += gentypeStr[ii+1] + ' ' + group + '\n'
        groupcount[group] += 1


    data_arr += [[pid, group]] #not quite accurate for gammas?
    if savefig:
        funcs.plotclasses(ax, stimuli, palphas, pbetas_all, betastr=betastr,betacol = betacol)
        fname = os.path.join(savedir,condition + '-' + gentypeStr_p + '-' + str(pid) + '.png')
        ax.text(.9,1.25,str(pid))
        ax.text(-.9,1.0,printstr)    
        f.savefig(fname, bbox_inches='tight', transparent=False)
        plt.cla()

print(groupcount)
data = pd.DataFrame(columns=('participant','betagroup'),data = data_arr)
#print(data)
with open('individual_group_counts.p','wb') as f:
    pickle.dump(data,f)
