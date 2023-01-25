import sqlite3, sys, os
import pandas as pd
import numpy as np

os.chdir(sys.path[0])

pd.set_option('display.width', 120, 'display.precision', 2)

con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
counterbalance = pd.read_sql_query("SELECT * from counterbalance", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

print(participants.shape)

# counts per condition
#print(participants.groupby('condition').size())
print(participants.groupby(['condition','gentype']).size())


participants = pd.merge(participants, counterbalance, on = 'counterbalance')
print(pd.pivot_table(
    data = participants,
    columns = 'xax',
    index = 'condition',
    aggfunc = 'size'
    ))



stats = pd.merge(stats, participants, on = 'participant')
from scipy.stats import ttest_ind, mannwhitneyu, ttest_rel
cols = ['area','between','within',
                'correlation', 
                'drange', 'xrange', 'yrange', 'xstd', 'ystd']
conds = ['C0','C1','C2','R0','R1','R2','X0','X1','X2']
for i in cols:
    gs = list(stats.groupby('condition')[i])
    gs = list(stats.groupby(['condition','gentype'])[i])
    d = dict(gs)
    ms = dict([(k, np.mean(v)) for k,v in d.items()])
    #p = mannwhitneyu(d['Middle'], d['Bottom']).pvalue

    S = i
    tempdict = {}
    for k,v in d.items():
        kstr = str(k[0][0]) + str(k[1])
        tempdict[kstr] = round(np.mean(v),3)
        #S += '\t' + kstr + ' = ' + str(round(np.mean(v),3))
    #S += '\t' + 'p = ' + str(round(p,3))
    for cond in conds:
        if cond in tempdict: 
            S += '\t' + cond + ' = ' + str(tempdict[cond])
        else:
            print('WARNING: fewer conds than expected')
    print(S)


for j, rows in stats.groupby('condition'):
    g1 = rows['within'].to_numpy()
    g2 = rows['between'].to_numpy()
    print(j, ttest_rel(g1, g2))

