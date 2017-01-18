# Modules

This is the directory containing custom modules for model classes and various utility functions. It can be imported by:

```python
import sys
sys.path.insert(0, "../../../Modules/") # generate-categories/Modules
from models import Optimize, CopyTweak, Packer, ConjugateJK13
import utils
```

Alternative methods of importing the modules may not work (based on my experience).

## Todo

- Make this module easier to import with. Use main module title from which `utils` and `models` can be imported (i.e., `from custom.models import ...`).
- Add `model.param_rvs` attribute to each model, specifying a random init parameterization. Allow this to be executed before initialization.
- Optimize `costfun()` so that probabilities are only evaluated once per unique category set.