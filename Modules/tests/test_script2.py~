import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(precision = 2, linewidth = 120)







execfile('Imports.py') 
from Modules.Classes import CopyTweak, Packer, ConjugateJK13
import Modules.Funcs as funcs

print dir(funcs)
lll

# [[72 73 74 75 76 77 78 79 80]
#  [63 64 65 66 67 68 69 70 71]
#  [54 55 56 57 58 59 60 61 62]
#  [45 46 47 48 49 50 51 52 53]
#  [36 37 38 39 40 41 42 43 44]
#  [27 28 29 30 31 32 33 34 35]
#  [18 19 20 21 22 23 24 25 26]
#  [ 9 10 11 12 13 14 15 16 17]
#  [ 0  1  2  3  4  5  6  7  8]]
stimuli = np.fliplr(funcs.ndspace(9,2))

categories = [
	stimuli[[10, 19, 28, 37],:],
	stimuli[[8,65],:],
	]

P = ConjugateJK13.rvs()
P['wts'] = 1.0 - np.array([0.7,0.3])
M = ConjugateJK13(categories,P)
print M