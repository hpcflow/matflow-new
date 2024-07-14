from pathlib import Path
from damask_parse.readers import read_HDF5_file
from damask_parse.utils import generate_viz


def process_HDF5(damask_hdf5_file, damask_post_processing, VE_response_data, damask_viz):
    VE_response = read_HDF5_file(
        hdf5_path=damask_hdf5_file,
        operations=damask_post_processing,
        **VE_response_data,
    )
    generate_viz(hdf5_path=damask_hdf5_file, viz_spec=damask_viz, parsed_outs=VE_response)

    return VE_response
