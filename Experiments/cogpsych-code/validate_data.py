s = 'Invalid data name supplied. Please select one of these options:'

choices = ['pooled',
           'pooled-no1st',
           'catassign',
           'xcr',
           'midbot',
           'nosofsky1986',
           'nosofsky1989',
           'NGPMG1994']


dataname = funcs.valData(dataname,s,choices)
pickledir = 'pickles/'
# Data
if dataname == 'pooled':
        # all data
        filename = 'all_data_e1_e2'
        task = "generate"
elif dataname == 'pooled-no1st':
        # trials 2-4
        filename = 'trials_2-4_e1_e2'
        task = "generate"
elif dataname == 'catassign':
        # trials 2-4
        filename = 'catassign'
        task = "assign"
elif dataname == 'xcr':
        # experiment 1 only XOR, Cluster, Row conditions
        filename = dataname
        task = "generate"
elif dataname == 'midbot':
        # experiment 2 only mid bottom conditions
        filename = dataname
        task = "generate"
elif dataname == 'nosofsky1986':
        # nosofsky data
        filename = dataname
        task = "assign"
elif dataname == 'nosofsky1989':
        # nosofsky data
        filename = dataname
        task = "assign"
elif dataname == 'NGPMG1994':
        # Nosofsky, Gluck, Palmeri, McKinley, and Glauthier 1994 data
        filename = dataname
        task = "error"
else:        
        raise Exception('Invalid data name specified.')

src = '{}.p'.format(filename)
dst = 'best_params_{}.p'.format(filename)
