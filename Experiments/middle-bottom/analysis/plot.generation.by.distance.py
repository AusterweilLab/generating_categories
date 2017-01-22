import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()

generation = pd.merge(generation, info, on = 'participant')

ngenerations = pd.DataFrame(dict(
	condition = [],
	stimulus = [],
	count = []
))

for c in pd.unique(info.condition):
	for i in range(stimuli.shape[0]):
		count = sum((generation.condition == c) & (generation.stimulus ==i))
		row = dict(condition = c, stimulus = i, count = count)
		ngenerations = ngenerations.append(row, ignore_index = True)



fh = plt.figure(figsize = (3.5,3))
condition_styles = dict(Middle = 'r-o', Bottom = 'b-o')
for i, (c, rows) in enumerate(ngenerations.groupby('condition')):

	As = stimuli[alphas[c],:]

	D = utils.pdist(stimuli, As)
	D = np.mean(D, axis = 1)
	
	x = np.unique(D)
	y = []
	e = []
	for j in x:
		nums = np.where(D == j)[0]
		curr_rows = rows.loc[rows.stimulus.isin(nums)]
		counts = curr_rows['count'].as_matrix()
		y.append(np.mean(counts))
		e.append(np.std(counts))
	print y
	plt.errorbar(x, y, yerr=e, fmt=condition_styles[c], label = c)

plt.gca().xaxis.grid(False)
# plt.axis([0.15, 1.35, -2, 34])

plt.legend(loc = 'upper left', frameon = True)
plt.xlabel('Distance From Alpha Category')
plt.ylabel('Generation Frequency')

fh.savefig('generation.by.distance.png', bbox_inches = 'tight')


		