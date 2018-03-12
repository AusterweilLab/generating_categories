#This script crawls through each cgi file and amends the header so that it runs appropriately.
#When running on Luke, and presumably a lot of other machines,, first line should be:
#! /bin/python
#When running on Xian's local machine (for testing etc)
#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import os
import re
# from os import listdir
from os.path import isfile, join

cgidir = 'webapp/cgi-bin'
headerchangedef = 'local'

#onlyfiles = [f for f in listdir(cgidir) if isfile(join(mypath, f))]

#Take in inputs from shell
if __name__ == "__main__":
    import sys
    if len(sys.argv)>1:
        headerchange = sys.argv[1];
    else:
        headerchange = headerchangedef
else:
    headerchange = headerchangedef; #default

#Serverheader
headerserver = '#! /bin/python';
headerlocal  = '#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python'; 

#Match line breaks
pattern = r'#!.*\n';#'(\r\n?|\n)+'

if headerchange == 'server':
    header = headerserver
elif headerchange == 'local':
    header = headerlocal
    
for file in os.listdir(cgidir):
    if file.endswith(".cgi"):
        with open(join(cgidir,file),'r') as readfile:
            fileStr = readfile.read()
        findMatch = [(m.start(0), m.end(0)) for m in re.finditer(pattern, fileStr)]
        #Assuming that end of last match is when the code begins
        if len(findMatch)>0:
            #startMatch = findMatch[0][0]
            endMatch = findMatch[-1][-1]
            strLength = len(fileStr)
            if fileStr[0:endMatch] == header+'\n':
                print('Header of ' + join(cgidir,file) + ' same as request, so not changed.')
            else:
                newfileStr = header + '\n' + fileStr[endMatch:strLength]
                with open(join(cgidir,file),'w') as writefile:
                    writefile.write(newfileStr)
                print('Changed header of ' + join(cgidir,file) + ' to ' + header)
                

            
                    

