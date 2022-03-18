import numpy as np
from hpcflow import HPCFlow

from matflow._version import __version__

MatFlow = HPCFlow(name="matflow", version=__version__)  # must be package name

# temporarily used just to check correct inclusion of numpy in built exes:
a = np.random.random((10, 10))
