s = 'Invalid data name supplied. Please select one of these options:'
choices = ['pooled','pooled-no1st','midbot','nosofsky1986','nosofsky1989','NGPMG1994']

dataname = funcs.valData(dataname,s,choices)
pickledir = 'pickles/'
# Data
if dataname == 'pooled':
        # all data
        src = "all_data_e1_e2.p"
        dst = "best_params_all_data_e1_e2.p"
        task = "generate"
elif dataname == 'pooled-no1st':
        # trials 2-4
        src = "trials_2-4_e1_e2.p"
        dst = "best_params_trials_2-4_e1_e2.p"
        task = "generate"
elif dataname == 'midbot':
        # experiment 2 only mid bottom conditions
        src = "midbot.p"
        dst = "best_params_midbot.p"
        task = "generate"
elif dataname == 'nosofsky1986':
        # nosofsky data
        src = "nosofsky1986.p"
        dst = "best_params_nosofsky1986.p"
        task = "assign"
elif dataname == 'nosofsky1989':
        # nosofsky data
        src = "nosofsky1989.p"
        dst = "best_params_nosofsky1989.p"
        task = "assign"
elif dataname == 'NGPMG1994':
        # Nosofsky, Gluck, Palmeri, McKinley, and Glauthier 1994 data
        src = "NGPMG1994.p"
        dst = "best_params_NGPMG1994.p"
        task = "error"
else:        
        raise Exception('Invalid data name specified.')
