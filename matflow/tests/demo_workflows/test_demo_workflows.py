from functools import partial

from matplotlib import pyplot as plt
import pytest

from scipy.stats import norm
from hpcflow.sdk.core.enums import EARStatus
import numpy as np

import matflow as mf
from matflow.tests.subset_simulation import (
    coarse_weight,
    generate_next_level_samples_DA,
    generate_next_level_samples_MLDA_incorrect,
    get_approx_y_star_random_walk,
    make_voxel_grouping,
    subset_simulation,
    generate_next_level_samples,
    system_analysis_toy_model,
    weakest_link_performance_coarse,
    weakest_link_performance_fine,
)


@pytest.mark.demo_workflows
def test_damask_input_files(tmp_path, save_fig, reference_array_data):
    """Test submission and check the stress-strain curve from a simple DAMASK workflow,
    with specific input files provided.

    Note this test must be run with a `--with-env-source /path/to/envs.yaml` option that
    points to an environment file with definitions for:
     - `damask_env`
     - `damask_parse_env`

    """
    mf.print_envs()
    mf.config._show(metadata=True)
    wk = mf.make_demo_workflow("damask_input_files", path=tmp_path)
    wk.submit(wait=True, add_to_known=False)

    runs = wk.get_all_EARs()
    assert all(run.status is EARStatus.success for run in runs)

    VE_response = wk.tasks.simulate_VE_loading_damask.elements[
        0
    ].outputs.VE_response.value
    STRAIN_KEY = "vol_avg_equivalent_strain"
    STRESS_KEY = "vol_avg_equivalent_stress"
    stress = VE_response["phase_data"][STRESS_KEY]["data"][:]
    strain = VE_response["phase_data"][STRAIN_KEY]["data"][:]

    fig, ax = plt.subplots()
    ax.plot(strain, stress)
    ax.set_xlabel(STRAIN_KEY)
    ax.set_ylabel(STRESS_KEY)

    # save figure to the --fig-dir (if passed, otherwise within `--basetemp`); and if run
    # with `--save-reference`, also save to the reference data folder:
    save_fig(fig, name="stress_strain.png")

    # save reference data (if run with `--save-reference`) or check it matches existing:
    reference_array_data(
        {"stress": stress, "strain": strain},
        name="stress_strain.npz",
        rtol=1e-10,
    )


@pytest.mark.demo_workflows
def test_subset_simulation_toy_model_prediction(tmp_path):
    """Validate the MatFlow subset simulation implementation for a toy model.

    Note this test must be run with a `--with-env-source /path/to/envs.yaml` option that
    points to an environment file with definitions for:
     - `damask_parse_env`

    """

    seed = 1234

    # run via a MatFlow workflow:
    wk = mf.make_and_submit_demo_workflow(
        "subset_simulation_toy_model",
        path=tmp_path,
        status=False,
        add_to_known=False,
        resources={"random_seed": seed},
    )

    # run via single function implementation:
    pf_sf, cov_sf, sus_acc_sf, mcmc_acc_sf = subset_simulation(
        dimension=200,
        target_pf=1e-4,
        p_0=0.1,
        num_samples=100,
        num_levels=7,
        sampling_method=generate_next_level_samples,
        sampling_method_kwargs={
            "proposal": norm(scale=1.0),
        },
        master_seed=seed,
        mimic_matflow=True,
    )

    wk.wait()
    final_iter = wk.tasks.collate_results.elements[0].latest_iteration_non_skipped
    pf = final_iter.get("outputs.pf")
    cov = final_iter.get("outputs.cov")
    sus_acc = final_iter.get("outputs.accept_rate")[:]

    # TODO: also verify same result with `subset_simulation_toy_model_external`, once
    # that can be submitted without a ridiculous number of processes.

    assert pf == pf_sf
    assert cov == cov_sf
    assert np.allclose(sus_acc, sus_acc_sf)
    # TODO: store and check mcmc_accept


@pytest.mark.demo_workflows
def test_subset_simulation_toy_model_DA_prediction(tmp_path):
    """Validate the MatFlow delayed acceptance subset simulation implementation for a toy
    model.

    Note this test must be run with a `--with-env-source /path/to/envs.yaml` option that
    points to an environment file with definitions for:
     - `damask_parse_env`

    """

    seed = 123
    NUM_LEVELS = 4

    # run via a MatFlow workflow:
    wk = mf.make_and_submit_demo_workflow(
        "subset_simulation_toy_model_DA",
        path=tmp_path,
        status=False,
        add_to_known=False,
        resources={"random_seed": seed},
    )

    proposal = norm()
    dimension = 200
    block_size = 10
    target_pf = 1e-4

    COST_RATIO = 1 / block_size

    y_star = get_approx_y_star_random_walk(
        sigma=1, dimension=dimension, target_pf=target_pf
    )

    group_idx = make_voxel_grouping(dimension, block_size)

    performance = partial(weakest_link_performance_fine, y_star=y_star)
    performance_coarse = partial(
        weakest_link_performance_coarse, y_star=y_star, group_idx=group_idx
    )

    debug = subset_simulation(
        performance=performance,
        dimension=dimension,
        p_0=0.1,
        num_samples=100,
        num_levels=NUM_LEVELS,
        master_seed=seed,
        sampling_method=generate_next_level_samples_DA,
        sampling_method_kwargs={
            "proposal": proposal,
            "temperature": 1,
            "performance_coarse": performance_coarse,
            "coarse_weight": coarse_weight,
            # "coarse_weight": lambda *args, **kwargs: 1,
            "num_inner_states": 3,
            "spawn_key": (5,),
        },
        transformation=lambda x: np.cumsum(x, axis=-1),  # random walk model
        debug=True,
        mimic_matflow=True,
    )

    wk.wait()

    iter_i = wk.tasks.collate_results.elements[0].iterations[-1]
    assert iter_i.get("outputs.pf") == debug["pf"]
    assert iter_i.get("outputs.cov") == debug["cov"]
    assert iter_i.get("outputs.threshold") == debug["thresholds"][-1]


@pytest.mark.demo_workflows
def test_subset_simulation_toy_model_two_level_prediction(tmp_path):
    """Validate the MatFlow MLDA subset simulation implementation for a toy model.

    Note this test must be run with a `--with-env-source /path/to/envs.yaml` option that
    points to an environment file with definitions for:
     - `damask_parse_env`

    """

    def get_final_RNG_states(wk, level=0):
        chain_rngs = []
        for chain_element in wk.tasks.generate_next_state.elements:
            for iter_i in chain_element.iterations:
                if iter_i.loop_skipped:
                    continue
                if (
                    iter_i.loop_idx["levels"] == level
                    and iter_i.loop_idx["inner_markov_chain"]
                    == wk.loops.inner_markov_chain.num_iterations - 1
                    and iter_i.loop_idx["outer_markov_chain"]
                    == wk.loops.outer_markov_chain.num_iterations - 1
                ):
                    chain_rngs.append(
                        iter_i.get("outputs.rng").bit_generator.state["state"]["state"]
                    )
        return chain_rngs

    def get_x_original(wk):
        return np.array([i.value[:] for i in wk.tasks.sample_direct_MC.outputs.x])

    def get_all_g_inc_out(wk, level=0):
        all_gs = []
        for element in wk.tasks.increment_chain.elements:
            for iter_i in element.iterations:
                if iter_i.loop_skipped:
                    continue
                if (
                    iter_i.loop_idx["levels"] == level
                    and iter_i.loop_idx["outer_markov_chain"]
                    == wk.loops.outer_markov_chain.num_iterations - 1
                ):
                    all_gs.append(iter_i.get("outputs.all_g")[:])
        return np.array(all_gs)

    def get_collate_outputs(wk, level=0):
        for iter_i in wk.tasks.collate_results.elements[0].iterations:
            if iter_i.loop_skipped:
                continue
            if iter_i.loop_idx["levels"] == level:
                return {
                    k: v[:] if k in ("chain_seeds", "chain_g") else v
                    for k, v in iter_i.get("outputs").items()
                    if k
                    in (
                        "level_pf",
                        "level_cov",
                        "num_failed",
                        "threshold",
                        "chain_seeds",
                        "chain_g",
                        "pf",
                    )
                }

    def get_current_and_trial_x_inner(wk, level=0):
        all_x_current = []
        all_x_trial = []

        for element in wk.tasks.generate_next_state.elements:
            all_x_current_chain_i = []
            all_x_trial_chain_i = []
            for iter_i in element.iterations:
                # TODO: are iterations ordered sensibly?
                if iter_i.loop_idx["levels"] == level:
                    all_x_current_chain_i.append(iter_i.get("inputs.x"))
                    all_x_trial_chain_i.append(iter_i.get("outputs.x"))

            all_x_current.append(all_x_current_chain_i)
            all_x_trial.append(all_x_trial_chain_i)

        return np.array(all_x_current), np.array(all_x_trial)

    def get_inc_inner_inputs(wk, chain_idx, outer_idx, inner_idx, level=0):

        element = wk.tasks.increment_chain_inner.elements[chain_idx]
        for iter_i in element.iterations:
            if iter_i.loop_skipped:
                continue
            if (
                iter_i.loop_idx["levels"] == level
                and iter_i.loop_idx["outer_markov_chain"] == outer_idx
                and iter_i.loop_idx["inner_markov_chain"] == inner_idx
            ):
                threshold = iter_i.get("inputs.threshold")
                all_x = iter_i.get("inputs.all_x")
                all_g = iter_i.get("inputs.all_g")
                all_x_inner = iter_i.get("inputs.all_x_inner")
                all_g_inner = iter_i.get("inputs.all_g_inner")

                first_inner = False
                if all_x_inner is None:
                    first_inner = True
                    # first "inner" iteration, need to set initial value:
                    all_x_inner = np.array(all_x[-1])[None]
                    all_g_inner = np.array([all_g[-1]])
                current_x = all_x_inner[-1]
                current_g = all_g_inner[-1]
                trial_x = iter_i.get("inputs.x")[:]
                trial_g = iter_i.get("inputs.g")
                is_accept = trial_g > threshold

                new_x = trial_x if is_accept else current_x
                new_g = trial_g if is_accept else current_g

                return {
                    "first_inner": first_inner,
                    "current_x_SUM": np.sum(current_x),
                    "current_g": current_g,
                    "trial_x_SUM": np.sum(trial_x),
                    "trial_g": trial_g,
                    "threshold": threshold,
                    "is_accept": is_accept,
                    "new_x_SUM": np.sum(new_x),
                    "new_g": new_g,
                    "data_idx(trial_x)": iter_i.get_data_idx("inputs.x"),
                }

    def get_result(wk):
        final_iter = wk.tasks.collate_results.elements[0].latest_iteration_non_skipped
        return {
            "pf": final_iter.get("outputs.pf"),
            "cov": final_iter.get("outputs.cov"),
        }

    seed = 1234
    NUM_LEVELS = 4
    level_idx = NUM_LEVELS - 1

    # run via a MatFlow workflow:
    wk = mf.make_and_submit_demo_workflow(
        "subset_simulation_toy_model_two_level",
        path=tmp_path,
        status=False,
        add_to_known=False,
        resources={"random_seed": seed},
    )
    dimension = 200
    performance = partial(system_analysis_toy_model, dimension=dimension, target_pf=1e-4)

    # run via single function implementation:
    debug = subset_simulation(
        performance=performance,
        dimension=dimension,
        p_0=0.1,
        num_samples=100,
        num_levels=NUM_LEVELS,
        sampling_method=generate_next_level_samples_MLDA_incorrect,
        sampling_method_kwargs={
            "performance_coarse": performance,
            "proposal": norm(scale=1.0),
            "num_coarse_states": 4,
        },
        master_seed=seed,
        mimic_matflow=True,
        debug=True,
    )

    wk.wait()

    x_original = get_x_original(wk)
    chain_rngs = get_final_RNG_states(wk, level=level_idx - 1)
    all_g_inc_out = get_all_g_inc_out(wk, level=level_idx - 1)
    collate_outs = get_collate_outputs(wk, level=level_idx)
    current_x_inner, trial_x_inner = get_current_and_trial_x_inner(wk, level=level_idx)
    result = get_result(wk)

    # original sampled states are identical:
    assert np.array_equal(x_original, debug["x_original"])

    # chain RNGs are identical:
    assert debug["debug_chain_states"] == chain_rngs

    # level outputs are identical:
    assert (level_pf := collate_outs["level_pf"]) == debug["level_pf"]
    assert (level_cov := collate_outs["level_cov"]) == debug["level_cov"]
    assert (num_failed := collate_outs["num_failed"]) == debug["num_failed"]
    assert (threshold := collate_outs["threshold"]) == debug["threshold"]
    assert (pf := collate_outs["pf"]) == debug["pf"]

    # seeds and g for input to next level chains are the same
    assert np.array_equal(np.array(debug["chain_seeds"]), collate_outs["chain_seeds"])
    assert np.array_equal(debug["chain_g"], collate_outs["chain_g"])

    # all_g - (num_chains, num_states) are the same
    assert np.array_equal(all_g_inc_out, debug["all_g"])

    print(f"{level_pf=!r}")
    print(f"{level_cov=!r}")
    print(f"{num_failed=!r}")
    print(f"{threshold=!r}")
    print(f"{pf=!r}")
