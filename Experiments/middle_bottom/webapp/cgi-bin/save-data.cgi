#! /bin/python

# get globals
execfile('config.py')
data = json.load(sys.stdin)

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This script takes as stdin a single participant's data and 
# saves it to a json file. 
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# save data as-is
participant = data['info']['participant']
datafile = os.path.join(destination, str(participant) + '.json')
with open(datafile, 'w') as f:
    json.dump(data, f)

