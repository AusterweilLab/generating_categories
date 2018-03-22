#Plot a scatterplot of average error vs model ll for each generated set (122 in midbot)
import sqlite3, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
colors = ["#34495e", "#e74c3c"]
sns.set_palette(colors)

execfile('Imports.py')
import Modules.Funcs as funcs


#Import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
assignment = pd.read_sql_query("SELECT * from assignment", con)
goodnessE = pd.read_sql_query("SELECT * from goodnessExemplars", con)
goodnessC = pd.read_sql_query("SELECT * from goodnessCategories", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con).as_matrix()
#stats = pd.read_sql_query("SELECT * from betastats", con)
con.close()

