from pathlib import Path
from typing import Dict

from damask_parse.readers import read_HDF5_file


def process_damask_HDF5(damask_hdf5_file: Path, damask_post_processing: Dict):
    _ = read_HDF5_file(hdf5_path=damask_hdf5_file, operations=damask_post_processing)
    return None
