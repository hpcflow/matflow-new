from pathlib import Path
from typing import Dict, List, Union

from damask_parse.utils import generate_viz


def viz_damask_HDF5(
    damask_hdf5_file: Path,
    damask_viz: Union[Dict, List],
    VE_response: Dict,
):
    generate_viz(hdf5_path=damask_hdf5_file, viz_spec=damask_viz, parsed_outs=VE_response)
