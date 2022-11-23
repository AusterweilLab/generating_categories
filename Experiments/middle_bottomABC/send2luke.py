#Package up webapp dir and send to server (Luke)

import os, sys

localdir = 'webapp'
serverdirbase = '/var/services/web/experiments/'
serverdir = 'catgen_midbotABC'

#tarzip local
os.system('tar -cvzf {}.tar.gz {}'.format(localdir,localdir))
#scp it over 
os.system('scp -i ~/Dropbox/.ssh/luke -P 1202 {}.tar.gz xian@alab.psych.wisc.edu:{}'.format(localdir,serverdirbase))

#mk new dir on host and untar the tar
cdcmd = 'cd {}'.format(serverdirbase)
untarcmd = 'tar -xvzf {}.tar.gz '.format(localdir)
renamecmd = 'mv {} {}'.format(localdir,serverdir)
#rm the tar
removecmd = 'rm {}.tar.gz'.format(localdir)
#run it all
os.system('ssh -i ~/Dropbox/.ssh/luke -p 1202 -t xian@alab.psych.wisc.edu  \'{};{};{};{}\' '.format(cdcmd,untarcmd,renamecmd,removecmd))

