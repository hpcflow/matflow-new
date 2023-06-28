from pathlib import Path
from typing import Dict
from damask_parse.readers import read_HDF5_file


def extract_damask_HDF5(damask_hdf5_file: Path, VE_response_data: Dict):
    VE_response = read_HDF5_file(hdf5_path=damask_hdf5_file, **VE_response_data)
    return VE_response
