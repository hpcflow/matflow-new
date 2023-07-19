import copy
import numpy as np
from damask import Grid
from damask_parse.utils import validate_volume_element, validate_orientations


def generate_volume_element_random_voronoi(
    microstructure_seeds,
    VE_grid_size,
    homog_label,
    orientations,
):
    grid_obj = Grid.from_Voronoi_tessellation(
        cells=np.array(VE_grid_size),
        size=np.array(microstructure_seeds["size"]),
        seeds=np.array(microstructure_seeds["position"]),
        periodic=True,
    )
    # TODO: this needs some more thought.

    if orientations is None:
        oris = copy.deepcopy(microstructure_seeds["orientations"])

    else:
        # see `LatticeDirection` enum:
        align_lookup = {
            "a": "a",
            "b": "b",
            "c": "c",
            "a_star": "a*",
            "b_star": "b*",
            "c_star": "c*",
        }
        unit_cell_alignment = {
            "x": align_lookup[orientations.unit_cell_alignment.x.name],
            "y": align_lookup[orientations.unit_cell_alignment.y.name],
            "z": align_lookup[orientations.unit_cell_alignment.z.name],
        }
        oris = {
            "type": "quat",
            "quaternions": np.array(orientations.data),
            "quat_component_ordering": "scalar-vector",
            "unit_cell_alignment": unit_cell_alignment,
        }
    oris = validate_orientations(oris)

    num_grains = len(microstructure_seeds["position"])
    const_phase_lab = np.array(microstructure_seeds["phase_labels"])[
        np.zeros(num_grains, dtype=int)
    ]

    ori_idx = np.arange(num_grains)

    volume_element = {
        "size": grid_obj.size.astype(float).tolist(),
        "grid_size": grid_obj.cells.tolist(),
        "orientations": oris,
        "element_material_idx": grid_obj.material,
        "constituent_material_idx": np.arange(num_grains),
        "constituent_material_fraction": np.ones(num_grains),
        "constituent_phase_label": const_phase_lab,
        "constituent_orientation_idx": ori_idx,
        "material_homog": np.full(num_grains, homog_label),
    }
    volume_element = validate_volume_element(volume_element)
    return {"volume_element": volume_element}
