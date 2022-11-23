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
print(participants.groupby('condition').size())
print 

participants = pd.merge(participants, counterbalance, on = 'counterbalance')
print pd.pivot_table(
	data = participants,
	columns = 'xax',
	index = 'condition',
	aggfunc = 'size'
	)