from matflow.param_classes import LoadCase


def test_single_multistep_uniaxial():
    args = {
        "num_increments": 200,
        "total_time": 100,
        "direction": "x",
        "target_def_grad_rate": 1e-3,
    }
    lc1 = LoadCase.uniaxial(**args)
    lc2 = LoadCase.multistep(steps=[{"type": "uniaxial", **args}])
    assert lc1 == lc2
