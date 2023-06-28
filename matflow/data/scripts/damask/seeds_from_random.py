from damask import seeds
from damask import Rotation
import numpy as np


def seeds_from_random(
    VE_size,
    num_grains,
    phase_label,
    orientation_coordinate_system=None,
):

    VE_size = np.array(VE_size)
    position = seeds.from_random(VE_size, num_grains)
    rotation = Rotation.from_random(shape=(num_grains,))
    out = {
        "microstructure_seeds": {
            "position": position,
            "orientations": {
                "type": "quat",
                "quaternions": rotation.quaternion,
                "quat_component_ordering": "scalar-vector",
                "orientation_coordinate_system": orientation_coordinate_system,
                "unit_cell_alignment": {
                    "x": "a",
                    "z": "c",
                },
                "P": -1,
            },
            "size": VE_size,
            "random_seed": None,
            "phase_labels": [phase_label],
        }
    }
    return out
