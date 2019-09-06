s = 'Invalid data name supplied. Please select one of these options:'

choices = ['pooled',
           'pooled-no1st',
           '5con',
           '5con_s',
           'catassign',
           'xcr',
           'xcrABC',
           'xcrA',
           'xcrB',
           'xcrC',
           'midbot',
           'midbotABC',
           'corner',
           'corner_s',
           'corner_c',
           'nosofsky1986',
           'nosofsky1989',
           'NGPMG1994']


dataname = funcs.valData(dataname,s,choices)
pickledir = 'pickles/'
raw_db = ''
# Data
if dataname == 'pooled':
        # compiled data from xcr and midbot
        filename = 'all_data_e1_e2'
        raw_db = 'experiments.db'
        task = "generate"
elif dataname == 'pooled-no1st':
        # compiled data from xcr and midbot, trials 2-4
        filename = 'trials_2-4_e1_e2'
        task = "generate"
elif dataname == '5con':
        # compiled data from xcr, midbot, and corner, including circles in the corner condition
        filename = dataname
        raw_db = 'experiment-5con.db'
        task = 'generate'
elif dataname == '5con_s':
        # compiled data from xcr, midbot, and corner, excluding circles in corner condition (so only squares in whole dataset)
        filename = dataname
        raw_db = 'experiment-5con_s.db'
        task = 'generate'
elif dataname == 'catassign':
        # category learning from experiment 2
        filename = 'catassign'
        raw_db = 'experiment-midbot.db'
        task = "assign"
elif dataname == 'catassign_err':
        # category learning from experiment 2 
        filename = 'catassign'
        raw_db = 'experiment-midbot.db'
        task = "error"
elif dataname == 'xcr':
        # experiment 1 only XOR, Cluster, Row conditions
        filename = dataname
        raw_db = 'experiment-xcr.db'
        task = "generate"
elif dataname == 'xcrABC':
        # XOR, Cluster, Row conditions with Not-Alpha, Beta-only, Beta-Gamma conditions
        filename = dataname
        raw_db = 'experiment-xcrABC.db'
        task = "generate"
elif dataname == 'xcrA':
        # XOR, Cluster, Row conditions with Not-Alpha condition
        filename = dataname
        raw_db = 'experiment-xcrA.db'
        task = "generate"
elif dataname == 'xcrB':
        # XOR, Cluster, Row conditions with Beta-only condition
        filename = dataname
        raw_db = 'experiment-xcrB.db'
        task = "generate"
elif dataname == 'xcrC':
        # XOR, Cluster, Row conditions with Beta-Gamma condition
        filename = dataname
        raw_db = 'experiment-xcrC.db'
        task = "generate"        
elif dataname == 'midbot':
        # experiment 2 only mid bottom conditions
        filename = dataname
        raw_db = 'experiment-midbot.db'
        task = "generate"
elif dataname == 'corner':
        # corner condition, with squares and shepard circles
        filename = dataname
        raw_db = 'experiment-corner.db'
        task = "generate"
elif dataname == 'corner_s':
        # corner condition, with squares only
        filename = dataname
        raw_db = 'experiment-corner_s.db'
        task = "generate"
elif dataname == 'corner_c':
        # corner condition, with shepard circles only
        filename = dataname
        raw_db = 'experiment-corner_c.db'
        task = "generate"
elif dataname == 'midbotABC':
        # Middle and Bottom conditions with Not-Alpha, Beta-only, Beta-Gamma conditions
        filename = dataname
        raw_db = 'experiment-midbotABC.db'
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
bestparmchtc = 'chtc_gs_best_params_{}.p'.format(filename)
