from damask_parse.utils import volume_element_from_2D_microstructure


def generate_volume_element_extrusion(
    microstructure_image,
    depth,
    image_axes,
    homog_label,
    phase_label,
    phase_label_mapping,
):
    volume_element = volume_element_from_2D_microstructure(
        microstructure_image=microstructure_image,
        homog_label=homog_label,
        phase_label=phase_label,
        phase_label_mapping=phase_label_mapping,
        depth=depth,
        image_axes=image_axes,
    )
    volume_element["grid_size"] = tuple(int(i) for i in volume_element["grid_size"])
    volume_element["size"] = tuple(float(i) for i in volume_element["size"])
    return {"volume_element": volume_element}
