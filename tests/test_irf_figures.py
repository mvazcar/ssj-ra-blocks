import numpy as np

from rbc_rank_blocks.workflow import reference_shock
from rbc_rank_blocks.irf_figures import (
    export_output_irf_figures,
    output_response_percent,
)
from rbc_rank_blocks.models import build_all_models


def _models_and_impulses(horizon=24):
    models = build_all_models()
    impulses = {}
    for name, bundle in models.items():
        shock, path = reference_shock(bundle, horizon)
        impulses[name] = bundle.solve_impulse_linear({shock: path})
    return models, impulses


def test_output_normalization_and_controlled_comparisons():
    models, impulses = _models_and_impulses()
    output = {
        name: output_response_percent(bundle, impulses[name])
        for name, bundle in models.items()
    }
    assert np.isclose(
        output["rbc"][0],
        100 * impulses["rbc"]["Y"][0] / models["rbc"].steady_state["Y"],
    )
    assert output["rbc"][0] > 0
    assert np.allclose(
        output["rank_calvo_sticky_prices"],
        output["rank_rotemberg_sticky_prices"],
        atol=1e-12,
    )
    assert output["rank_union_sticky_wages"][0] < 0
    assert output["rank_firm_sticky_wages"][0] > 0


def test_irf_comparison_artifacts_are_synchronized(tmp_path):
    models, impulses = _models_and_impulses()
    paths = export_output_irf_figures(models, impulses, tmp_path, max_period=20)
    assert set(paths) == {"rbc", "price", "wage", "index"}
    for path in paths.values():
        assert path.exists()

    rbc = paths["rbc"].read_text(encoding="utf-8")
    price = paths["price"].read_text(encoding="utf-8")
    wage = paths["wage"].read_text(encoding="utf-8")
    index = paths["index"].read_text(encoding="utf-8")
    assert "RBC output response" in rbc
    assert "#0072BD" in price and "#D95319" in price
    assert "stroke-dasharray" in price and "stroke-dasharray" in wage
    assert "Helvetica" in rbc and "Helvetica" in price and "Helvetica" in wage
    assert 'stroke-opacity="0.16"' in price
    assert 'font-size="34"' in price and 'stroke-width="5.5"' in price
    assert "Calvo prices" in price and "Rotemberg prices" in price
    assert "Union wages" in wage and "Firm wages" in wage
    assert "three retained figures" in index
    assert "full-system IRF" in index
