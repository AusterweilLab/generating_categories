import pandas as pd
from collections import OrderedDict
import numpy as np
import csv
from time import strptime, mktime

# quick function to read csv as list of lists
def csv2lists(p):
	with open(p, 'r') as f:
		reader = csv.reader(f)
		return list(reader)

# make all possible columns numeric
def numberize(df):
	return df.apply(lambda x: pd.to_numeric(x, errors='ignore'))

# store all Condition assignments
Conditions = pd.DataFrame(
	columns = ['XOR',	'Cluster',	'Row'], 
	index = range(4),
	data = 	[
			 [ 0,  6,  1],
			 [10,  8,  3],
			 [70, 24,  5],
			 [80, 26,  7],]
	)

condition_order = ['XOR',	'Cluster',	'Row']


class Participant(object):
	timeformat = "%d %b %Y %I:%M:%S %p"
	phase_cols = dict(
		training = ['condition','participant','phase','block','trial',
					'stimulus','Size','Color','rt'],
		generate = ['condition','participant','phase',None,'trial',
							'stimulus','Size','Color','rt'],
		generalization = ['condition','participant','phase','trial',
						  'stimulus','Size','Color','response','rt']
		)	

	def __init__(self, filepath, nrows = 100):

		# store raw data
		self.filepath = filepath
		self.raw_data = csv2lists(filepath)

		# check if data file has all the rows
		if len(self.raw_data) != nrows:
			self.complete = False
			return
		else: self.complete = True
			
		# parse info from top rows
		info_rows = self.raw_data[:3]		
		self.startstr       = info_rows[0][0].strip()
		self.finishstr      = info_rows[0][-1].strip()
		self.running_pc     = info_rows[1][0].strip()
		self.participant    = int(info_rows[1][1])
		self.condition_num  = int(info_rows[1][2]) - 1
		self.counterbalance = int(info_rows[2][0])

		# set up classification info
		self.condition = condition_order[self.condition_num]	
		self.alphas = Conditions[self.condition]

		# add data for each phase
		for phase, cols in self.phase_cols.items():
			rows = self.__phase_getter(phase)
			df = pd.DataFrame(rows, columns = cols)
			df = numberize(df)
			setattr(self, phase, df)	

		# manual corrections
		self.generate = self.generate.dropna(axis=1, how='all')
		self.__rename('generate', 'generation')

		self.training.stimulus -= 1
		self.generation.stimulus -= 1
		self.generalization.stimulus -= 1

		self.start  = int(mktime(strptime(self.startstr, self.timeformat)))
		self.finish = int(mktime(strptime(self.finishstr, self.timeformat)))


	def __phase_getter(self, phase):
		"""return phase rows from the raw data"""
		return [i for i in self.raw_data if i[2] == phase]

	# rename self property
	def __rename(self, old, new):
	    setattr(self, new, getattr(self, old))
	    delattr(self, old)

	def attrs2dict(self, attrs):
		res = dict()
		for j in attrs:
			res[j] =  getattr(self, j)
		return res


