from damask import __version__
from damask_parse.writers import write_load_case


def write_load(path, load_case, damask_solver):
    load_steps = []
    for step in load_case.steps:
        dct = step.to_dict()
        dct["def_grad_aim"] = dct.pop("target_def_grad", None)
        dct["def_grad_rate"] = dct.pop("target_def_grad_rate", None)
        load_steps.append(dct)

    write_load_case(
        dir_path=path.parent,
        load_cases=load_steps,
        solver=damask_solver,
        name=path.name,
        write_2D_arrs=(__version__ != "3.0.0-alpha3"),
    )
