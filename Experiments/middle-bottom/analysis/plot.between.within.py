import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
import utils

pd.set_option('precision', 2)
np.set_printoptions(precision = 2)

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT participant, condition from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
generation = pd.read_sql_query("SELECT * from generation", con)
alphas = pd.read_sql_query("SELECT * from alphas", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
con.close()


stats = pd.merge(stats, info, on = 'participant')
stats['more_within'] = stats['within'] > stats['between']

# plot between and within scatter
fh = plt.figure(figsize = (3,3))
plt.plot([0, 2],[0,2], '--', color = 'gray', linewidth = 0.5)
condition_styles = dict(Middle = 'r', Bottom = 'b')
for c, rows in stats.groupby('condition'):

	rows.plot(x = 'within', y= 'between', kind = 'scatter', ax = fh.gca(),
		c = condition_styles[c], alpha = 0.5, label = c)
	
plt.gca().grid(False)
plt.axis([0., 1.5, 0., 1.5])

plt.legend(loc = 'lower right', frameon = True)
plt.xlabel('Within Category Distance')
plt.ylabel('Between Category Distance')
plt.xticks(np.linspace(0, 1.5,6))
plt.yticks(np.linspace(0, 1.5,6))
# fh.savefig('between.within.png', bbox_inches = 'tight')


# do some stats
groups = stats.groupby(['condition', 'more_within'])
cols = ['area','xrange', 'yrange', 'within', 'between']
print groups[cols].mean()


corners = [0, 8, 72, 80]
generation['corners'] = generation.stimulus.isin(corners)

table = generation.groupby('participant')['corners'].sum().reset_index()
table = pd.merge(table, stats[['participant', 'condition', 'more_within']],
								 on = 'participant')


print pd.pivot_table(
	data=table, 
	index = 'condition', 
	columns = 'more_within',
	values = 'corners',
	aggfunc = 'mean'
	)


from scipy.stats import ttest_ind, mannwhitneyu

g1 = table.loc[table.more_within == True, 'corners']
g2 = table.loc[table.more_within == False, 'corners']
print mannwhitneyu(g1, g2)

for c, rows in table.groupby('condition'):
	g1 = rows.loc[rows.more_within == True, 'corners']
	g2 = rows.loc[rows.more_within == False, 'corners']
	print c, mannwhitneyu(g1, g2)

idx = (table.condition == 'Bottom') & (table.more_within == True)
g1 = table.loc[idx, 'corners']
idx = (table.condition == 'Middle') & (table.more_within == True)
g2 = table.loc[idx, 'corners']
print mannwhitneyu(g1, g2)
print ttest_ind(g1, g2)


