#Remotely compresses the finished pickles and brings them back to local 
import sys
import os
from datetime import datetime
fetchdirbase = 'gencat'
fetchdir = fetchdirbase
narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    fetchdir = sys.argv[1]

suffix = fetchdir[len(fetchdirbase):]
    
tz = 'cd {};tar -cvzf allpickles{}.tar.gz pickles*'.format(fetchdir,suffix) #compress files
datestr = datetime.now().strftime("%d%m%y")

os.system('ssh -i ~/Dropbox/.ssh/chtc -t liew2@submit-1.chtc.wisc.edu \'{}\' '.format(tz))
os.system('scp -i ~/Dropbox/.ssh/chtc liew2@submit-1.chtc.wisc.edu:{}/allpickles{}.tar.gz ./chtctar/private/allpickles{}{}.tar.gz'.format(fetchdir,suffix,suffix,datestr))

#Run chtc analysis
print('Extracting chtc pickles...')
os.system('python analyse_chtc.py allpickles{}{}.tar.gz'.format(suffix,datestr))
print('Chtc pickles extracted - you should be able to see it in the pickles directory now.')
