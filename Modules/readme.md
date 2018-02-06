# Modules

This is the directory containing custom modules for model classes and various utility functions. To use the modules, you need to append the base directory of this repository (`generating-categories/`) to the system path.

If you know where that is relative to your script, then you can do:

```python
import sys
sys.path.insert(0, "generate-categories/") # or wherever this is!
from Modules.Classes import CopyTweak, Packer, ConjugateJK13, Optimize
import Modules.Funcs as funcs
```

If you don't want to keep track, I have written an `Imports.py` script that finds the main directory (assumed to be a parent directory ) and inserts it into the system path. `Imports.py` can be copied to wherever you are scripting so that you can do this:

```python
execfile('Imports.py') 
from Modules.Classes import ...
...
```

## How simulation works here

To run the model fits, try this (in the cogpsych-code folder)

```
python global-model-fits.py 
```
One of the key elements of understanding how the models are simulated is understanding the structure of the Trialset object. 

Contained in the Simulation module, `Trialset(stimuli)` creates an object that contains a bunch of information on the set of trials shown to all participants, as well as all responses provided on each trial (given some full set of stimuli). It needs to be fed the raw data in terms of a data frame (see Experiments/cogpsych-code/construct-trial-set.py, lines 30-31 (correct as of Feb 5 2018)). I’ll leave a description of an appropriate data frame for a future writeup.

Let’s say we have a Trialset object `ts`. One of the key bits of `ts` is the Set attribute.  The Set attribute contains information on all unique trials (where a unique trial is defined as a unique set of exemplars in each category) and all responses (i.e., generated exemplars). For instance, when I do this:

```python
>>> ts.Set[3] #just starting from some arbitrary index here, since the indices appear arbitrary
```

I may be returned something like:

```python
{'response': [76, 79, 80, 77], 'categories': [array([10, 12, 14, 16]), array([75])]}
```

This means that in the entire data set, trials which contained Category A (reflecting the condition) exemplars 10, 12, 14, and 16, and Category B (generated) exemplar 75, elicited responses from 4 participants. One participant generated exemplar 76, another generated 79, a third generated 80, and the fourth generated 77. 

By the way, the exemplar numbers represent their indices on this 2D mapping:

```python 
[[72 73 74 75 76 77 78 79 80]
 [63 64 65 66 67 68 69 70 71]
 [54 55 56 57 58 59 60 61 62]
 [45 46 47 48 49 50 51 52 53]
 [36 37 38 39 40 41 42 43 44]
 [27 28 29 30 31 32 33 34 35]
 [18 19 20 21 22 23 24 25 26]
 [ 9 10 11 12 13 14 15 16 17]
 [ 0  1  2  3  4  5  6  7  8]]
```

Since someone responded with 76 on one trial, then there must exist some other unique trial `i` where `ts.Set[i]['categories']` returns
```python
[array([10, 12, 14, 16]), array([75, 76])]
```
Indeed, that does exist (when I enter `ts.Set[4]['categories']`). 

The model fits themselves are performed by the `hillclimber()` function in `Simulation.py`. It maximises the loglikelihoods for a given model. The loglikelihood calculations are actually initiated in the `Trialset.loglike(params, model)` method (evidently it takes in the parameters (as a list) and the model object as input arguments). This method retrieves the probability of each observed response on a unique trial. Specifically, see the line

```python
	ps = model(categories, params).get_generation_ps(self.stimuli,1)
```

The `get_generation_ps()` method is defined in the `Model` abstract base class, but really specified in each individual model's code. For exemplar models (like Packer and CopyTweak), this method computes the similarities between exemplars and all stimuli. 

Note that the irrelevant comparisons are filtered out at a later stage in the `loglike()` method — see the line that goes `ps = ps[trial['response']]`. The probabilities determined for each response to each unique trial are converted to loglikelihoods and summed across all trials and responses. This value is then maximised by `op.minimise` (well, more correctly the _negative_ log likelihood is minimized). The rest should be fairly self explanatory.


## Todo

- Optimize `costfun()` so that probabilities are only evaluated once per unique category set.
- Use things like `**kwargs` to make plotting functions more flexible.
- Do something to behave appropriately when the user asks to simulate a category that is more than 1+ the max.
