#Fetch data from server (Luke)

import os, sys

zipfile = 'data.tar.gz'
serverdir = "/var/services/homes/xian/CloudStation/data/xor-cluster-rowABC"
#serverdir = os.path.join(serverdirbase,serverdir) #main working dir on server
#SSH into server and tarzip data
cdcmd = 'cd {}'.format(serverdir)
tarcmd = 'tar -cvzf {} ./*'.format(zipfile)
os.system('ssh -i ~/Dropbox/.ssh/luke -p 1202 -t xian@alab.psych.wisc.edu \'{};{}\''.format(cdcmd,tarcmd))
#Fetch tarzipped data
os.system('scp -i ~/Dropbox/.ssh/luke -P 1202 xian@alab.psych.wisc.edu:{} data/'.format(os.path.join(serverdir,zipfile)))
#untar data
os.system('tar -xvzf data/{} -C data/'.format(zipfile))        
print 'Data extracted to the data folder. Feel free to compile by going into the analysis folder and running \'python compile.py\'.'
