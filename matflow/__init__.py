from hpcflow import HPCFlow
from matflow._version import __version__

MatFlow = HPCFlow(name="matflow", version=__version__)  # must be package name
