import sqlite3
import pandas as pd

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

stats = pd.merge(stats, info[['participant', 'condition']], on = 'participant')

print 'Raw counts for table:'
for condition, rows in stats.groupby('condition'):
	print condition
	g = rows.groupby(['top_used', 'bottom_used']).size().reset_index()
	print pd.pivot_table(g, index = 'top_used', columns = 'bottom_used')


from scipy.stats import fisher_exact

for i in ['top_used', 'bottom_used', 'top_and_bottom', 'bottom_only', 'top_only']:
	g = stats.groupby(['condition', i]).size().reset_index()
	c = pd.pivot_table(g, index = 'condition', columns = i, fill_value=0)
	pval = fisher_exact(c)[1]
	pval = round(pval,4)
	print 'Fishers exact test comparing groups on: ' + i + '\t\tp = ' + str(pval)
	print c


