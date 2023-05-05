import numpy as np
from ruamel.yaml import YAML
from damask_parse.utils import validate_volume_element


def validate_constituent_material_idx(constituent_material_idx):
    cmi_range = np.arange(0, np.max(constituent_material_idx) + 1)
    if np.setdiff1d(cmi_range, constituent_material_idx).size:
        msg = (
            f"The unique values (material indices) in `constituent_material_idx` "
            f"should form an integer range. This is because the distinct materials "
            f"are defined implicitly through other index arrays in the volume "
            f"element."
        )
        raise ValueError(msg)


def get_material_constituent_idx(constituent_material_idx):
    validate_constituent_material_idx(constituent_material_idx)
    material_constituent_idx = []
    for mat_idx in np.unique(constituent_material_idx):
        mat_const_idx_i = np.where(np.isin(constituent_material_idx, mat_idx))[0]
        material_constituent_idx.append(mat_const_idx_i)

    return material_constituent_idx


def get_volume_element_materials(volume_element, homog_schemes=None, phases=None, P=-1):

    volume_element = validate_volume_element(
        volume_element,
        homog_schemes=homog_schemes,
        phases=phases,
    )

    const_mat_idx = volume_element["constituent_material_idx"]
    mat_const_idx = get_material_constituent_idx(const_mat_idx)

    all_quats = volume_element["orientations"]["quaternions"]

    quat_comp_order = volume_element["orientations"].get("quat_component_ordering")
    if quat_comp_order != "scalar-vector":
        msg = (
            f"Quaternion component ordering (`quat_component_ordering`) should be "
            f'"scalar-vector", as adopted by DAMASK, but it is actually '
            f'"{quat_comp_order}"'
        )
        raise RuntimeError(msg)

    const_mat_frac = volume_element["constituent_material_fraction"]
    const_ori_idx = volume_element["constituent_orientation_idx"]
    const_phase_lab = volume_element["constituent_phase_label"]

    materials = []
    for mat_idx, mat_i_const_idx in enumerate(mat_const_idx):

        mat_i_constituents = []
        for const_idx in mat_i_const_idx:
            mat_i_const_j_phase = str(const_phase_lab[const_idx])
            mat_i_const_j_ori = all_quats[const_ori_idx[const_idx]]

            if phases[mat_i_const_j_phase]["lattice"] == "hP":

                if "unit_cell_alignment" not in volume_element["orientations"]:
                    msg = "Orientation `unit_cell_alignment` must be specified."
                    raise ValueError(msg)

                if volume_element["orientations"]["unit_cell_alignment"].get("y") == "b":
                    raise NotImplementedError("nope")

                elif (
                    volume_element["orientations"]["unit_cell_alignment"].get("x") != "a"
                ):
                    msg = (
                        f"Cannot convert from the following specified unit cell "
                        f"alignment to DAMASK-compatible unit cell alignment (x//a): "
                        f'{volume_element["orientations"]["unit_cell_alignment"]}'
                    )
                    NotImplementedError(msg)

            if volume_element["orientations"]["P"] != P:
                # Make output quaternions consistent with desired "P" convention, as
                # determined by `P` argument:
                mat_i_const_j_ori[1:] *= -1

            mat_i_const_j = {
                "v": float(const_mat_frac[const_idx]),
                "O": mat_i_const_j_ori.tolist(),  # list of native float or np.longdouble
                "phase": mat_i_const_j_phase,
            }
            mat_i_constituents.append(mat_i_const_j)

        materials.append(
            {
                "homogenization": str(volume_element["material_homog"][mat_idx]),
                "constituents": mat_i_constituents,
            }
        )

    return materials


def write_material(path, volume_element, homogenization, phase):
    materials = get_volume_element_materials(
        volume_element,
        homog_schemes=homogenization,
        phases=phase,
        P=-1,  # DAMASK uses P = -1 convention.
    )

    # Only include phases that are used:
    phase = {
        phase_name: phase_data
        for phase_name, phase_data in phase.items()
        if phase_name in volume_element["constituent_phase_label"]
    }

    mat_dat = {
        "phase": phase,
        "homogenization": homogenization,
        "material": materials,
    }
    yaml = YAML()
    yaml.dump(mat_dat, path)
