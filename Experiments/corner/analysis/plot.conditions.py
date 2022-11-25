import sqlite3, sys
import numpy as np
import pandas as pd
import os,sys

os.chdir(sys.path[0])

np.set_printoptions(precision = 1)

import matplotlib.pyplot as plt

exec(open('Imports.py').read())
import Modules.Funcs as funcs


con = sqlite3.connect('../data/experiment.db')
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()
alphas = pd.read_sql_query("SELECT * from alphas", con)
con.close()

#panel_labs = ['(a)','(b)','(c)','(d)']

# plot categories
f, ax = plt.subplots(1, 1, figsize=(2, 1.5))
#alphas = ['Corner']
#Rename column and remove one of them (because we don't differentiate between circles and squares at this point)
del alphas['Corner_C']
alphas.rename(columns = {'Corner_S':'Corner'},inplace=True)

for i, k  in enumerate(list(alphas)):
    h = ax
    #lab = panel_labs[i+1]
    funcs.plotclasses(h, stimuli, alphas[k], [])        

    h.axis(np.array([-1, 1, -1, 1])*1.25)
    # h.text(-1.1, 1.1, k, ha = 'left', va = 'top')
    title = k
    h.set_title(title)
    [i.set_linewidth(0.5) for i in iter(h.spines.values())]


# plot stimulus domain
# h = ax[0]
#lab = panel_labs[0]
#squares = funcs.ndspace(50, 2, low = 0.0)

# set color
# colmax, colmin = 230.0 / 255.0, 25.0 / 255.0
# squares[:,0] = (squares[:,0] * (colmax - colmin) + colmin)

# # set size
# sizmax, sizmin = 5.8, 3.0
# squares[:,1] = squares[:,1] * (sizmax-sizmin) + sizmin # size
# squares[:,1] *= 3.5

# for i in [0,8,72,80]:#[0, 49, 2450, 2499]:
#     col, siz = squares[i,:]
#     x, y  = stimuli[i,:]
#     h.plot(x, y, 's', ls = '-', mec = 'k', mew = 0.5,
#         mfc = [col, col, col], ms = siz
#         )

# h.set_title(lab + ' Stimulus Space')
# h.axis(np.array([-1, 1, -1, 1])*1.5)
# h.set_xticks([])
# h.set_xlabel('Size')
# h.set_ylabel('Color')

# h.set_yticks([])

# h.set_aspect('equal', adjustable='box')
# [i.set_linewidth(0.5) for i in h.spines.itervalues()]

f.savefig('conditions.pdf', bbox_inches='tight', transparent=False)

#path = '../../../Manuscripts/cog-psych/figs/e1-conditions.pgf'
#funcs.save_as_pgf(f, path)
