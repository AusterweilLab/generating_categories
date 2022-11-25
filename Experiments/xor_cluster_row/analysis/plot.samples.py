import sqlite3, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
os.chdir(sys.path[0])

exec(open('Imports.py').read())
import Modules.Funcs as funcs

pd.set_option('display.precision', 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).to_numpy()

con.close()

textsettings = dict(fontsize = 6)

# ASSIGN SUBPLOTS TO CONDITIONS
#  		 CLUSTER   		 #      	  ROW      		 #      	  XOR         #
#  0		 1		 2  	 3     4     5  	 6 	 	 7     8     9  	 10
# 11		12		13		14		15		16		17		18		19		20		 21
# 22		23		24		25		26		27		28		29		30		31		 32

assignments  = {

	# CLUSTER
	 '0': 0,  '1': 17,  '2': 41, # Clusters
	'11': 10, '22': 15, # Column
	'12': 6,  '23': 27, # Row
	'13': 22, '24': 121, # Corner

	# ROW
	 '4':  4,  '5': 14,  '6': 24, # ROWS
	'15': 29, '16': 60, '17': 86, # ROWS
	'26': 37, '27': 50, '28': 233, # clusters

	# XOR
	 '8': 46,  '9': 75, '10': 84, # anti-xor
	'19': 111, '20': 113, '21': 240, # with-xor
	'30': 42, '31': 83, '32': 116, # clusters

	# nothing
	'empty':[3,14,25,7,18,29]

}

P, E = 2, 0.2
gridspec_kw = {'width_ratios':[P,P,P, E, P,P,P, E, P,P,P]}

# plotting
fig, ax= plt.subplots(3,11, figsize=np.array([7.,2.3]) , gridspec_kw = gridspec_kw)
ax_flat = ax.flatten()
for i, h in enumerate(ax_flat):

	if i in assignments['empty']: 
		h.axis('off')
		continue
	

	# get condition
	# get participant
	pid = assignments[str(i)]
	curr_cond = list(info.loc[info.participant == pid, 'condition'])[0]

	As = alphas[curr_cond].to_numpy()
	Bs = generation.loc[generation.participant == pid, 'stimulus']

	funcs.plotclasses(h, stimuli, As, Bs, textsettings = textsettings)

	if i in [1, 5, 9]:
		h.set_title(curr_cond)

fig.subplots_adjust(wspace = 0.09, hspace = 0.01)
fig.savefig('samples.pdf', bbox_inches='tight', transparent=False)


# path = '../../../Manuscripts/cog-psych/figs/e1-samples.pgf'
# funcs.save_as_pgf(fig, path)

