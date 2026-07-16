import numpy as np
import pytest

from rbc_rank_blocks.blocks import PRICE_CARTRIDGES, WAGE_CARTRIDGES
from rbc_rank_blocks.calibration import (
    calvo_marginal_cost_slope,
    rank_price_calibration,
)
from rbc_rank_blocks.models import build_all_models


def test_price_cartridges_have_identical_ssj_contracts():
    calvo = PRICE_CARTRIDGES["calvo"]
    rotemberg = PRICE_CARTRIDGES["rotemberg"]
    assert list(calvo.inputs) == list(rotemberg.inputs)
    assert list(calvo.outputs) == list(rotemberg.outputs)


def test_wage_cartridges_have_identical_pairwise_ssj_contracts():
    monopoly = WAGE_CARTRIDGES["monopoly"]
    monopsony = WAGE_CARTRIDGES["monopsony"]
    assert len(monopoly) == len(monopsony) == 2
    for worker_block, employer_block in zip(monopoly, monopsony):
        assert list(worker_block.inputs) == list(employer_block.inputs)
        assert list(worker_block.outputs) == list(employer_block.outputs)


def test_default_rotemberg_slope_matches_calvo_first_order():
    calibration = rank_price_calibration()
    rotemberg_slope = (calibration["epsilon_p"] - 1) / calibration["psi_p"]
    assert np.isclose(rotemberg_slope, calvo_marginal_cost_slope(calibration))


@pytest.mark.parametrize(
    ("shock_name", "impact", "persistence"),
    (
        ("a", 0.01, 0.90),
        ("z", 0.01, 0.50),
        ("nu", 0.0025, 0.50),
    ),
)
def test_matched_price_cartridges_have_identical_irfs_for_every_source_shock(
    shock_name,
    impact,
    persistence,
):
    models = build_all_models()
    shock = {shock_name: impact * persistence ** np.arange(80)}
    calvo = models["rank_calvo_sticky_prices"].solve_impulse_linear(shock)
    rotemberg = models["rank_rotemberg_sticky_prices"].solve_impulse_linear(shock)
    for variable in ("x", "y", "pi_p", "i", "mc_gap"):
        assert np.allclose(calvo[variable], rotemberg[variable], rtol=0.0, atol=1e-12)
    assert np.max(np.abs(calvo["mc_identity_error"])) < 1e-12
    assert np.max(np.abs(rotemberg["mc_identity_error"])) < 1e-12


def test_wage_phillips_slopes_have_opposite_signs():
    models = build_all_models()
    assert models["rank_union_sticky_wages"].steady_state["kappa_w"] > 0
    assert models["rank_firm_sticky_wages"].steady_state["kappa_w"] < 0


def test_wage_slopes_equal_the_documented_source_formulas():
    models = build_all_models()
    union = models["rank_union_sticky_wages"].steady_state
    firm = models["rank_firm_sticky_wages"].steady_state

    calvo_term = (1 - union["beta"] * union["theta_w"]) * (
        1 - union["theta_w"]
    ) / union["theta_w"]
    activity = union["sigma"] * (1 - union["alpha"]) + union["phi"] + union["alpha"]
    expected_union = calvo_term * activity / (
        1 + union["phi"] * union["epsilon_w"]
    )
    expected_firm = -calvo_term * activity / (1 + firm["alpha"] * firm["eta"])

    assert np.isclose(union["kappa_w"], expected_union)
    assert np.isclose(firm["kappa_w"], expected_firm)
