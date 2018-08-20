#Creates the working.tar.gz file and sends it to the specified directory on chtc
#Xian wrote this code and it'd probably be most useful to him - if you're not
#him you might want to edit the ssh permissions and stuff.
import sys
import os
send2dir = 'gencat'
narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    send2dir = sys.argv[1]

execfile('build_chtc.py')
os.chdir('../../..')
os.system('scp -i ~/Dropbox/.ssh/chtc working.tar.gz liew2@submit-5.chtc.wisc.edu:{}'.format(send2dir))
os.system('ssh -i ~/Dropbox/.ssh/chtc liew2@submit-5.chtc.wisc.edu')

