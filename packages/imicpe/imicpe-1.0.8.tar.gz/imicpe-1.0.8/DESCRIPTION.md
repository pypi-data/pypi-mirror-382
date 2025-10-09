
A toolbox used for practical sessions at [CPE Lyon](https://www.cpe.fr/).
Developped and maintained for teaching usage only!

# Installation

## In a Jupyter Notebook

```!pip install -U imicpe```

## In a local environment

```pip install -U imicpe```

# Usage example

The example below uses the mse method available in the `optim.metrics` subpackage of `imicpe`.

```python
import numpy as np
from imicpe.optim import metrics
N=10000

x=np.random.randn(1,N)
ref = np.zeros((1,N)) 
mse=metrics.mse(x,ref)   

print(mse)
```