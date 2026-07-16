import json
from pathlib import Path

from rbc_rank_blocks.dag import dag_spec, export_dag
from rbc_rank_blocks.models import build_all_models
from rbc_rank_blocks.provenance import BLOCK_SOURCES


def test_every_live_block_has_equation_provenance():
    for bundle in build_all_models().values():
        assert set(bundle.block_names) <= set(BLOCK_SOURCES)


def test_dag_spec_is_inferred_from_live_ssj_blocks():
    bundle = build_all_models()["rank_calvo_sticky_prices"]
    spec = dag_spec(bundle)
    assert [row["name"] for row in spec["blocks"]] == list(bundle.block_names)
    assert {node["id"] for node in spec["nodes"]} >= {
        "unknown:x",
        "unknown:pi_p",
        "shock:nu",
        "block:price_calvo",
        "target:price_residual",
    }
    assert any(
        edge["from"] == "block:price_core_diagnostics"
        and edge["to"] == "block:price_calvo"
        and set(edge["variables"]) == {"mc_gap", "mc_slope"}
        and not edge["interface_only"]
        for edge in spec["edges"]
    )


def test_rbc_dag_metadata_uses_gali_preference_names():
    spec = dag_spec(build_all_models()["rbc"])
    declared = spec["calibration"]["declared_values"]
    live = spec["calibration"]["live_parameter_values"]

    assert {"sigma", "phi"} <= declared.keys()
    assert {"sigma", "phi", "chi"} <= live.keys()
    assert not {"eis", "frisch", "psi", "inv_frisch", "vphi"} & live.keys()


def test_socket_only_inputs_are_not_presented_as_economic_dependencies():
    spec = dag_spec(build_all_models()["rank_firm_sticky_wages"])
    assert any(
        edge["from"] == "block:wage_activity"
        and edge["to"] == "block:labor_supply_monopsony"
        and edge["variables"] == ["labor_demand_coefficient"]
        and edge["interface_only"]
        for edge in spec["edges"]
    )


def test_all_three_dag_views_export_from_one_spec(tmp_path):
    bundle = build_all_models()["rank_firm_sticky_wages"]
    paths = export_dag(bundle, tmp_path)
    assert set(paths) == {"json", "mermaid", "svg"}
    spec = json.loads(paths["json"].read_text(encoding="utf-8"))
    mermaid = paths["mermaid"].read_text(encoding="utf-8")
    svg = paths["svg"].read_text(encoding="utf-8")
    for block in bundle.block_names:
        assert block in mermaid
        assert block in svg
    assert spec["model"] == bundle.name
    assert spec["display_name"] == "RANK - Firm sticky wages"
    assert spec["mechanism_status"] == bundle.mechanism_status
    assert "canonical_status" not in spec
    assert spec["calibration"]["status"] == bundle.calibration_profile.status
    assert spec["calibration"]["live_parameter_values"]["eta"] == 4.0
    assert "labor_supply_monopsony" in svg
    assert "Helvetica" in svg
    assert "#0072BD" in mermaid and "#D95319" in mermaid


def test_download_manifest_has_pinned_commits_and_checksums():
    manifest_path = Path(__file__).parents[1] / "sources" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert {row["name"] for row in manifest["repositories"]} == {
        "sequence-jacobian",
        "annual-review",
        "DSGE_mod",
    }
    assert all(len(row["commit"]) == 40 for row in manifest["repositories"])
    assert all(len(row["sha256"]) == 64 for row in manifest["files"])
    assert "ehl_1999_ifdp640.pdf" in {row["name"] for row in manifest["files"]}
    assert len({row["name"] for row in manifest["repositories"]}) == len(
        manifest["repositories"]
    )
    assert len({row["name"] for row in manifest["files"]}) == len(manifest["files"])
    assert all(Path(row["name"]).name == row["name"] for row in manifest["files"])


def test_code_provenance_uses_pinned_links_not_moving_branches():
    urls = [source.url for source in BLOCK_SOURCES.values()]
    assert not any("/blob/master/" in url or "/blob/main/" in url for url in urls)
