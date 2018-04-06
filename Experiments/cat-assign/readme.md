# Directory structure

Like any website, index.html is first loaded on entry.
Importantly, it loads a bunch of key variables in the
`variables.js` script. It then runs a check on the worker
(to see if it's on some banned list; see `checkworker()` in
`js/server.js`. `checkworker()` is first called in
`preview.html`) and then if it passes, the participant
details are assigned (workerId, assignment number,
condition, and counterbalance condition) and the experiment
is truly started up (`startup()` in `experiment.js`).

`startup()` loads a bunch of trial templates (the html files
in `/templates`) and starts running it, beginning with the
observation trials (`observation.js`). This also creates a
new data file (for each new participant) that is saved in
some data directory (this happens when the `savedata()`
function is run. The function is written in the server.js
file). And it also creates the stimuli
(`stimuli.make_stimuli`, which can be found in the
`stimuli.js` file)).

# First-time set up

If this is the first time you're setting up this experiment
to run, you're going to need to do a few things to get this
to run. First,  set up a database in another
directory (e.g. using phpMyAdmin). Here are the
specifications:
Database name: Workers
Table: 
 - Name: Workers
 - Column1: workerId
 - Column2: Paradigm
 - Column3: UnixTime
 - Column4: Experiment
 - Column5: Stimuli
 
The author (Xian) is following in Nolan's footsteps and placing this
experiment on Mechanical Turk through the python boto
package. I suppose you could go and manually work through
the swamp that is the AMT website (right now as of 090318
at least), but I've found working through boto to be much
easier. Anyway, to get this working, you'll need: 

1. An AMT requester account, which you should link to 
2. An AMT AWS account (I think it stands for amazon web
 services).	
3. I also strongly recommmend testing on a sandbox account
 first, so get that too.


With an AWS account, get the access keys and place them
into a .boto file in your home directory. There should be
clearer tutorials on this out there, I'd recommend googling
if none of this makes sense. You can then test the
connection by running the aws-python/check_connection.py
script. If the url in the script is set to the sandbox
account, you should see $10,000 printed in the console.
Otherwise, it should be your actual account balance.

# Data Structure

Raw individual data is stored in the data/ folder. This
is compiled by `compile.py` in the analysis folder into a
database named `experiment.db`. 

Data to be used in this experiment, but that is not actually
generated from this experiment, is placed in the
data_utilities/ folder. There's another readme in there that
should provide more information.

The allocation of participant numbers can also be confusing.
There are three layers here:
1. The original ppt number assigned in the original
   experiment (midbot). This should be typically labeled as
   "Old ID" or something.
2. Some new number that is the result of matching of the
   original/old ppt number to this new number. The mapping
   can be obtained by using at the `getMatched.py` in
   Modules/Funcs. For instance, if you have some new ppt
   number 20 and you want to see whose data it is in the old
   scheme, run `getMatched(20,db)` where db is the location
   of the `cmp_midbot.db` file, probably somewhere in
   data_utilities\ folder.
3. The raw ppt number that is displayed on the individual js
   files in the data\ folder. This is arbitrarily assigned
   in the order that participants arrive on the website to
   work on the task. 

# Notes

Before publishing, remember to change these variables:

1. For each cgi file restore the first line to be `#!
/bin/python` -- the nifty `prepare4server.py` file handles
this now. From a shell, run something like:
```bash
$ python prepare4server.py server
```
to change the header to `#! /bin/python`. Using `local`
instead of `server` as the first argument will set the
header to something appropriate for your local machine (for
Xian's it's
`#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python`.
(There's probably some easy way to fix that on my local
system, but I haven't had the time to try that yet.)

This script should also restore the right path to data on server
(around line 11) in `config.py` .

2. Check that condition names match in `config.py` (probably
near line 20) and that the counterbalance number in the next
line is appropriate

Also, remember to check where the Workers db is saved in
Luke. I'm guessing this is a list of workers we want to
block - check with Nolan. - ok got it. It can be accessed
through the phpmyadmin mariadb5 server

3. Add the `assignments.db` and `cmp_midbot.db` (if using
   middle-bottom conditions, otherwise is `cmp_xcr.db`) to
   the server data folder. This is NOT the one on mariadb,
   but rather somewhere like here: 
   /var/services/homes/xian/CloudStation/data/generate-categories
   
   Permissions have to be set appropriately in that folder.

