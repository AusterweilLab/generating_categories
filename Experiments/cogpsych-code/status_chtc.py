#Check status of chtc run
import sys
import os
from datetime import datetime
fetchdirbase = 'gencat'
fetchdir = fetchdirbase
narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    fetchdir = sys.argv[1]
cmd = 'condor_q; cd {};cat output/gencat*.err;'.format(fetchdir)
os.system('ssh -i ~/Dropbox/.ssh/chtc -t liew2@submit-1.chtc.wisc.edu \'{}\' '.format(cmd))
