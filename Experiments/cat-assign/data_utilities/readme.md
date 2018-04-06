Data here is a little messy, but I'll try to clarify what's going on here.

There are three sets of basic data files: 
1. `xcr.db` - Data from experiment 1 (as in the cogpsych manuscript), where participants are tested on the XOR, Cluster,
   and Row conditions.
   
2. `midbot.db` - Data from experiment 2 (as in the cogpsych manuscript, where participants are tested on the Middle and
   Bottom conditions.
3. `all.db` - Data from both experiments that have been pooled together using the compile-data.py script in the same
   directory.
   
   
Running `construct-trial-set.py` will create pickled data in the pickles folder.
