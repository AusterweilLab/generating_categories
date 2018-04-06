# Experiments

This directory contains code for running and analyzing the behavioral experiments. Files pertaining to each experiment are contained in a separate subdirectory.

The experiment is currently up at this link:

https://alab.psych.wisc.edu/experiments/generate-categories/?assignmentId=12ALONGRANDOMCHARACTERSTRING34&hitId=56ALONGRANDOMCHARACTERSTRING78&workerId=NOLANDEBUG123&turkSubmitTo=https%3A%2F%2Fworkersandbox.mturk.com

## Data structures

The data is a little haphazardly thrown around, especially after the cat-assign experiment, but I'll try to point out
the key bits. Raw experiment data will always be assigned to the data/ folder in the experiment's home directory. Some
kind of `compile.py` script in the analysis/ folder (also in experiment's home directory) will take the individual data
from Data/ and compile it into some usable database form, probably named `experiment.db`. 

The data in the cat-assign folder is a little more complex. See readme there for more info.


## Things to Explore

- ~~I want to see a plot of PACKER's log-likelihood as a function of the between-category parameter.~~ In progress as
  of 8 March 2018. See developments in the cogpsych-code/matlabtests directory. 

## Issues to fix with future experiments

1. RGB colors must be integer, but many of our RGB colors are floats (i.e., 100.5). I've just rounded them.
2. Save assignments and json in some other folder (not cloudstation).
3. Add lab marker to assignments database.
4. Add ajax statuses to data
5. Make sure user cannot zoom

## Known Data Weirdness

1. Sometimes the final 25 characters are appended twice to the end of the JSON data files? 
2. Some participants are not assigned a finish time, but are marked as complete. I think these may be the same as those with weird JSON above.
