import sqlite3, sys
import pandas as pd
import numpy as np

import os, sys
os.chdir(sys.path[0])

pd.set_option('display.width', 120)
pd.set_option('display.precision', 2)

con = sqlite3.connect('../data/experiment.db')
participants = pd.read_sql_query("SELECT * from participants", con)
counterbalance = pd.read_sql_query("SELECT * from counterbalance", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

print(participants.shape)

# counts per condition
print(participants.groupby('condition').size())

participants = pd.merge(participants, counterbalance, on = 'counterbalance')
print(pd.pivot_table(
	data = participants,
	columns = 'xax',
	index = 'condition',
	aggfunc = 'size'
	))