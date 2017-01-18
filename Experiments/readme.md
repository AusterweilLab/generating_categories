# Experiments

This directory contains code for running and analyzing the behavioral experiments. Files pertianing to each experiment are contained in a seperate subdirectory.

The experiment is currently up at this link:

https://alab.psych.wisc.edu/experiments/generate-categories/?assignmentId=12ALONGRANDOMCHARACTERSTRING34&hitId=56ALONGRANDOMCHARACTERSTRING78&workerId=NOLANDEBUG123&turkSubmitTo=https%3A%2F%2Fworkersandbox.mturk.com


## Issues

1. RGB colors must be integer, but in actuality our RGB colors involved decimals (i.e., 100.5). I've just rounded for now.
2. Save assignments and json in some other folder (not cloudstation).
3. Add lab marker to assignments database.
4. Add ajax status to data
5. Make sure user cannot zoom

## Data Weirdness

1. Sometimes the final 25 characters are appended twice to the end of the JSON data files? 
2. Some participants are not assigned a finish time, but are marked as complete. I think these may be the same as those with weird JSON above.