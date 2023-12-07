from damask_parse.utils import add_volume_element_buffer_zones


def add_VE_buffer_zones(
    volume_element,
    buffer_sizes,
    phase_ids,
    phase_labels,
    homog_label,
    order,
):
    volume_element = add_volume_element_buffer_zones(
        volume_element=volume_element,
        buffer_sizes=buffer_sizes,
        phase_ids=phase_ids,
        phase_labels=phase_labels,
        homog_label=homog_label,
        order=order,
    )
    volume_element["grid_size"] = tuple(int(i) for i in volume_element["grid_size"])
    volume_element["size"] = tuple(float(i) for i in volume_element["size"])
    return {"volume_element": volume_element}
