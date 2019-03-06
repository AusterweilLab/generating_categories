#Creates the working.tar.gz file and sends it to the specified directory on chtc
#Xian wrote this code and it'd probably be most useful to him - if you're not
#him you might want to edit the ssh permissions and stuff.
import sys
import os

send2dir = 'gencat'
narg = len(sys.argv)
if __name__ == "__main__" and narg>1:
    send2dir = sys.argv[1]

rmsubmit = 'cd {};./rmold_submitnew.sh'.format(send2dir) #this script on server removes old files and submits the new batch


execfile('build_chtc.py')
os.chdir('../../..')
#upload the new batch
print 'Uploading latest working batch to {}.'.format(send2dir)
os.system('scp -i ~/Dropbox/.ssh/chtc working.tar.gz liew2@submit-1.chtc.wisc.edu:{}'.format(send2dir))

#remotely remove the old files and submit
print 'Running rm and submit scripts on CHTC server...'
os.system('ssh -i ~/Dropbox/.ssh/chtc -t liew2@submit-1.chtc.wisc.edu \'{}\' '.format(rmsubmit))
#os.system('ssh -i ~/Dropbox/.ssh/chtc liew2@submit-5.chtc.wisc.edu')

