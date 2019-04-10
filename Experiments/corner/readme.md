This experiment tests category generation of squares and Shepard circles for the corner condition.

Link for quick testing:
http://alab.local/middle-bottomABC/webapp/?assignmentId=12ALONGRANDOMCHARACTERSTRING34&hitId=56ALONGRANDOMCHARACTERSTRING78&workerId=NOLANDEBUG123&turkSubmitTo=https%3A%2F%2Fworkersandbox.mturk.com

You may also have noticed some python files just hanging around here. I've written them to make the publishing of the
experiment and the retrieval of its data easier.

A brief description of them follow:

- fetchdata.py: This script fetches the data from the server (we call ours Luke). If you're using this script and
   running the experiment on your own server you would probably want to change the `serverdir` variable and the address
   of your server itself in the lines that run the ssh command.
 - prepare4server.py: This handy script changes the headers for the .cgi files so that they work appropriately on the
   server or the local machine. Somehow the way Xian has installed Python means that the header has to be in some form
   and that's different from how it is on Luke. Check out the script itself, I've commented it with a bit more detail
   there.
 - send2luke.py: This script compiles the relevant webapp directory, sends it to Luke, and extracts it to the public web
   directory there. Handy stuff. Like fetchdata.py, you may want to change the variables in this script so that it works
   on your own server with your own credentials.
   
    
