#Check status of chtc run
import sys
import os
from datetime import datetime
showerr = False
fetchdirbase = 'gencat'
fetchdir = fetchdirbase

narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    showerr = sys.argv[1]
    fetchdir = sys.argv[2]
    
cmd = 'condor_q;'
if showerr:
    cmd += 'cd {};cat output/gencat*.err;'.format(fetchdir)
    
os.system('ssh -i ~/Dropbox/.ssh/chtc -t liew2@submit-1.chtc.wisc.edu \'{}\' '.format(cmd))
