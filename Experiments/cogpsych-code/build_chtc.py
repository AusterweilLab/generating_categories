#Prepare tar.gz for upload to chtc
import os

# Navigate to one level above generating categories directory
currdir = os.getcwd()
finddir = 'generating-categories'
workingdir = 'chtc'
splitpath = os.path.split(os.getcwd())
while splitpath[1] != finddir:
    splitpath = os.path.split(splitpath[0])
    if splitpath == os.sep:
        S = 'Cannot find {} directory. You are here:\n\n {}'.format(finddir, os.getcwd)
        raise Exception(S)

path2dir = splitpath[0]
os.chdir(path2dir)
# Prepare directories
if not os.path.isdir(workingdir):
    os.mkdir(workingdir)
else:
    #remove directory and start afresh
    os.system('rm -r ' + workingdir)
    os.mkdir(workingdir)

if not os.path.isdir(os.path.join(workingdir,'Experiments')):
    os.mkdir(os.path.join(workingdir,'Experiments'))
# Copy generating-categories into new folder. Only include Modules and cogpsych code folder.
# Remember to exclude some folders like chtctar
os.system('rsync -av --progress '
          '--exclude={} --exclude={}  --exclude={} --exclude={} --exclude={} '
          '{} {} '.format('chtctar','chtc_code','*best_params*','matlabtests','*~',
                          os.path.join(finddir,'Experiments','cogpsych-code'),
                          os.path.join(workingdir,'Experiments'),
          ))
os.system('rsync -av --progress --exclude={} {} {}'.format('tests',
                                                           os.path.join(finddir,'Modules'),
                                                           os.path.join(workingdir)))

os.system('tar -cvzf working.tar.gz chtc' + os.sep)

os.chdir(currdir)
