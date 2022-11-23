import sqlite3, sys
import pandas as pd
import numpy as np

pd.set_option('display.width', 120, 'precision', 2)

con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
counterbalance = pd.read_sql_query("SELECT * from counterbalance", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

print participants.shape

# counts per condition
#print(participants.groupby('condition').size())
print(participants.groupby(['condition','gentype']).size())


participants = pd.merge(participants, counterbalance, on = 'counterbalance')
print pd.pivot_table(
    data = participants,
    columns = 'xax',
    index = 'condition',
    aggfunc = 'size'
    )



stats = pd.merge(stats, participants, on = 'participant')
from scipy.stats import ttest_ind, mannwhitneyu, ttest_rel
cols = ['area','between','within',
                'correlation', 
                'drange', 'xrange', 'yrange', 'xstd', 'ystd']
conds = ['B0','B1','B2','M0','M1','M2']
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
        S += '\t' + cond + ' = ' + str(tempdict[cond])
    print S


for j, rows in stats.groupby('condition'):
    g1 = rows['within'].as_matrix()
    g2 = rows['between'].as_matrix()
    print j, ttest_rel(g1, g2)

