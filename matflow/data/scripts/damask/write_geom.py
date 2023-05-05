from pathlib import Path

from damask import Grid
from damask_parse.utils import validate_volume_element


def write_geom(path, volume_element):

    volume_element = validate_volume_element(volume_element)
    element_material_idx = volume_element["element_material_idx"][:]
    ve_size = volume_element.get("size")
    ve_origin = volume_element.get("origin")
    if ve_size is None:
        ve_size = [1.0, 1.0, 1.0]
    if ve_origin is None:
        ve_origin = [0.0, 0.0, 0.0]

    ve_grid = Grid(material=element_material_idx, size=ve_size, origin=ve_origin)
    ve_grid.save(path)
