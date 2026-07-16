from dataclasses import replace

import numpy as np
import pytest

from rbc_rank_blocks.workflow import build_artifacts, reference_shock
from rbc_rank_blocks.models import MODEL_NAMES, build_all_models, build_model


EXPECTED_BLOCKS = {
    "rbc": {"rbc_firm", "rbc_household", "rbc_markets"},
    "rank_calvo_sticky_prices": {
        "natural_allocation",
        "output_identity",
        "price_core_diagnostics",
        "taylor_price",
        "dynamic_is",
        "price_calvo",
    },
    "rank_rotemberg_sticky_prices": {
        "natural_allocation",
        "output_identity",
        "price_core_diagnostics",
        "taylor_price",
        "dynamic_is",
        "price_rotemberg",
    },
    "rank_union_sticky_wages": {
        "wage_activity",
        "wage_output",
        "taylor_wage",
        "labor_demand_monopoly",
        "wage_pc_monopoly",
    },
    "rank_firm_sticky_wages": {
        "wage_activity",
        "wage_output",
        "taylor_wage",
        "labor_supply_monopsony",
        "wage_pc_monopsony",
    },
}


def test_registry_builds_expected_blocks_and_zero_steady_state_targets():
    models = build_all_models()
    assert tuple(models) == MODEL_NAMES
    for name, bundle in models.items():
        assert set(bundle.block_names) == EXPECTED_BLOCKS[name]
        for target in bundle.targets:
            assert abs(float(bundle.steady_state[target])) < 1e-10


def test_rbc_uses_gali_preference_notation_and_reciprocal_elasticities():
    bundle = build_all_models()["rbc"]
    inputs = {name for block in bundle.model.blocks for name in block.inputs}
    values = bundle.calibration_profile.values

    assert {"sigma", "phi", "chi"} <= inputs
    assert not {"eis", "frisch", "psi", "inv_frisch", "vphi"} & inputs
    assert values["sigma"] == 1.0
    assert values["phi"] == 1.0

    household = next(block for block in bundle.model.blocks if block.name == "rbc_household")
    steady_state = household.steady_state(
        {
            "K": 3.0,
            "L": 4.0,
            "w": 9.0,
            "sigma": 2.0,
            "phi": 0.5,
            "chi": 1.0,
            "delta": 0.1,
        }
    )
    assert steady_state["C"] == pytest.approx((9.0 / 4.0**0.5) ** (1.0 / 2.0))


def test_declared_shocks_match_the_documented_five_model_ladder():
    models = build_all_models()
    assert models["rbc"].exogenous == ("Z",)
    assert models["rank_calvo_sticky_prices"].exogenous == ("a", "z", "nu")
    assert models["rank_rotemberg_sticky_prices"].exogenous == ("a", "z", "nu")
    assert models["rank_union_sticky_wages"].exogenous == ("r_nat", "nu_w")
    assert models["rank_firm_sticky_wages"].exogenous == ("r_nat", "nu_w")


def test_every_model_solves_a_finite_linear_impulse():
    horizon = 60
    time = np.arange(horizon)
    models = build_all_models()
    shocks = {
        "rbc": {"Z": 0.01 * 0.9**time},
        "rank_calvo_sticky_prices": {"nu": 0.0025 * 0.5**time},
        "rank_rotemberg_sticky_prices": {"nu": 0.0025 * 0.5**time},
        "rank_union_sticky_wages": {"nu_w": 0.0025 * 0.5**time},
        "rank_firm_sticky_wages": {"nu_w": 0.0025 * 0.5**time},
    }
    for name, bundle in models.items():
        impulse = bundle.solve_impulse_linear(shocks[name])
        for unknown in bundle.unknowns:
            assert impulse[unknown].shape == (horizon,)
            assert np.isfinite(impulse[unknown]).all()


def test_dennery_policy_shock_reverses_labor_response():
    """A rate increase contracts demand but expands supply in the comparison."""

    models = build_all_models()
    shock = {"nu_w": 0.0025 * 0.5 ** np.arange(80)}
    monopoly = models["rank_union_sticky_wages"].solve_impulse_linear(shock)
    monopsony = models["rank_firm_sticky_wages"].solve_impulse_linear(shock)
    assert monopoly["l"][0] < 0
    assert monopsony["l"][0] > 0


def test_registry_rejects_undocumented_model_names():
    for name in ("rank_calvo", "rank_monopoly", "rank_price_calvo"):
        with pytest.raises(ValueError, match="Unknown model"):
            build_model(name)


def test_calibration_authority_is_explicit():
    models = build_all_models()
    assert (
        models["rank_calvo_sticky_prices"].calibration_profile.status
        == "canonical-textbook-calibration"
    )
    assert "canonical-foundation" in models[
        "rank_union_sticky_wages"
    ].calibration_profile.status
    assert "empirically-anchored" in models[
        "rank_firm_sticky_wages"
    ].calibration_profile.status
    assert models["rank_firm_sticky_wages"].calibration_profile.values["eta"] == 4.0


def test_linear_solution_scales_exactly_with_the_shock():
    for bundle in build_all_models().values():
        shock_name, shock_path = reference_shock(bundle, 80)
        baseline = bundle.solve_impulse_linear({shock_name: shock_path})
        doubled = bundle.solve_impulse_linear({shock_name: 2 * shock_path})
        for unknown in bundle.unknowns:
            assert np.allclose(
                doubled[unknown],
                2 * baseline[unknown],
                rtol=0.0,
                atol=1e-14,
            )


def test_early_irfs_are_stable_when_the_solution_horizon_doubles():
    for bundle in build_all_models().values():
        shock_80, path_80 = reference_shock(bundle, 80)
        shock_160, path_160 = reference_shock(bundle, 160)
        impulse_80 = bundle.solve_impulse_linear({shock_80: path_80})
        impulse_160 = bundle.solve_impulse_linear({shock_160: path_160})
        for unknown in bundle.unknowns:
            early_80 = impulse_80[unknown][:20]
            early_160 = impulse_160[unknown][:20]
            error = np.max(np.abs(early_80 - early_160))
            scale = max(np.max(np.abs(early_160)), 1e-30)
            assert error <= 2e-6 * scale + 1e-12


def test_invalid_family_and_short_horizon_fail_loudly(tmp_path):
    bundle = build_all_models()["rbc"]
    with pytest.raises(ValueError, match="at least 2"):
        reference_shock(bundle, 1)
    with pytest.raises(ValueError, match="Unknown model family"):
        reference_shock(replace(bundle, family="unknown"), 20)

    output = tmp_path / "should_not_exist"
    with pytest.raises(ValueError, match="at least 2"):
        build_artifacts(output, horizon=1)
    assert not output.exists()
