import numpy as np
from hpcflow import HPCFlowApp
from hpcflow.runtime import RunTimeInfo

from matflow._version import __version__

MatFlow = HPCFlowApp(
    name="matflow", version=__version__, description="Materials science workflow manager"
)

RUN_TIME_INFO = RunTimeInfo(__name__)

# temporarily used just to check correct inclusion of numpy in built exes:
a = np.random.random((10, 10))
