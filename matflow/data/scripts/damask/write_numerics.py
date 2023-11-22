from pathlib import Path
from damask_parse import write_numerics as write_numerics_


def write_numerics(path, damask_numerics):
    path = Path(path)
    write_numerics_(dir_path=path.parent, numerics=damask_numerics, name=path.name)
