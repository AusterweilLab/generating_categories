#Update all pickled experimental data files in the pickle folder. This is useful
# when I make changes to the structure of the trialset objects

execfile('construct-trial-set.py')
execfile('construct-trial-set-xcr.py')
execfile('construct-trial-set-midbot.py')
execfile('compile-data-catassign.py')
execfile('compile-data-nosofsky1986.py')
execfile('compile-data-nosofsky1989.py')
execfile('compile-data-NGPMG1994.py')
