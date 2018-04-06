This directory contains simulations and code for the Cognitive Psychology
submission that are not tied to any particular experiment.

# Running simulations

See the readme in the Modules folder for a brief description of the general
structure of the data and how it is applied in the fitting process.

To get the satisfaction of seeing something run, though, try entering this:

```python
python global-model-fits.py nosofsky1986
```

You can replace nosofsky1986 with the name of some other dataset. Probably check
the script itself for the most updated list, or enter something nonsensical and
choose form the menu that rolls out.

You can also supply two more arguments, first to fit the models to specific
participants, and second to fit to specific unique trials (e.g., in nosofsky1986
these are treated as separate conditions). For instance, running this will fit
the models to only participant 0's (i.e., the first participant's) condition 1
(i.e., criss cross condition) in the nosofsky1986 data:

```python
python global-model-fits.py nosofsky1986 0 1
```

## Grid search

You can run a grid search by running `global-model-grid-search.py` instead of
`global-model-fits.py` in the examples above. Input arguments (i.e., the data,
participant, and condition) should work in the same way for both scripts.
