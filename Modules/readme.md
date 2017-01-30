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
execfile('Import.py') 
from Modules.Classes import ...
...
```


## Todo

- Optimize `costfun()` so that probabilities are only evaluated once per unique category set.
- Use things like `**kwargs` to make plotting functions more flexible.
- Do something to behave appropriately when the user asks to simulate a category that is more than 1+ the max.