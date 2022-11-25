import sqlite3, os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
#  		 		MIDDLE   		 		 #      	  BOTTOM      		#
#  0		 1		 2  	 3     4     5  	 6 	 	 7     8  
#  9		10		11		12		13		14		15		16		17	
# 18		19		20		21		22		23		24		25		26		
# CL		ROW		COL 	4C 					CL		ROW		COL 	4C

assignments = {

	# Middle
  '0':   2,  '1':  7,  '2': 66,  '3':  1,
  '9':  62, '10': 27, '11': 24, '12': 43,
 '18': 157, '19': 82, '20': 78, '21': 44,

	'empty': np.array([4, 13, 22]),

	# Bottom
  '5': 22,  '6':  3,  '7': 10,  '8': 11,
 '14': 54, '15': 36, '16': 45, '17': 46,
 '23': 83, '24': 60, '25': 88, '26': 58
}


P, E = 2, 0.2
gridspec_kw = {'width_ratios':[P,P,P,P,  E,  P,P,P,P]}

# plotting
fig, ax= plt.subplots(3,9, figsize=np.array([6.4,2.3]) , gridspec_kw = gridspec_kw)
ax_flat = ax.flatten()
for i, h in enumerate(ax_flat):

	if i in assignments['empty']: 
		h.axis('off')
		continue
	
	# get participant
	pid = assignments[str(i)]
	curr_cond = list(info.loc[info.participant == pid, 'condition'])[0]

	As = alphas[curr_cond].as_matrix()
	Bs = generation.loc[generation.participant == pid, 'stimulus']

	funcs.plotclasses(h, stimuli, As, Bs, textsettings = textsettings)

	if i in [1, 6]:
		h.text(1.25, 1.4, curr_cond, va = 'bottom', ha = 'center', fontsize = 12)

	if i in   [18, 23]: xlab = 'Cluster'
	elif i in [19, 24]: xlab = 'Row'
	elif i in [20, 25]: xlab = 'Column'
	elif i in [21, 26]: xlab = 'Corners'
	if i in [18, 19, 20, 21, 23, 24, 25, 26]:
		h.set_xlabel(xlab, fontsize = 9)

# 18		19		20		21		22		23		24		25		26		
# CL		ROW		COL 	4C 					CL		ROW		COL 	4C

fig.subplots_adjust(wspace = 0.09, hspace = 0.01)
fig.savefig('samples.png', bbox_inches='tight', transparent=False)


path = '../../../Manuscripts/cog-psych/figs/e2-samples.pgf'
funcs.save_as_pgf(fig, path)

