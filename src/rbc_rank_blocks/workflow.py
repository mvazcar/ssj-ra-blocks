"""Reproducible smoke run and user-facing artifact generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from .dag import export_dag
from .irf_figures import export_output_irf_figures
from .models import ModelBundle, build_all_models
from .provenance import provenance_rows


def reference_shock(bundle: ModelBundle, horizon: int) -> tuple[str, np.ndarray]:
    """Return the transparent one-shock smoke test for a model family."""

    if horizon < 2:
        raise ValueError("horizon must be at least 2")
    time = np.arange(horizon)
    if bundle.family == "rbc":
        return "Z", 0.01 * 0.9**time
    if bundle.family == "rank_price":
        return "nu", 0.0025 * 0.5**time
    if bundle.family == "rank_wage":
        return "nu_w", 0.0025 * 0.5**time
    raise ValueError(f"Unknown model family {bundle.family!r}")


def _write_irf_csv(path: Path, impulse) -> None:
    keys = list(impulse.keys())
    horizon = len(impulse[keys[0]])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["t", *keys])
        for period in range(horizon):
            writer.writerow([period, *(float(impulse[key][period]) for key in keys)])


def _write_dag_index(directory: Path, models: dict[str, ModelBundle]) -> None:
    names = {name: bundle.display_name for name, bundle in models.items()}
    lines = [
        "# Generated SSJ DAGs",
        "",
        "Every figure below is generated from the live SSJ `inputs` and `outputs`",
        "of its assembled model. Parameter values are recorded in JSON and omitted from",
        "the visual arrows to keep the economic flows readable.",
        "",
        "## Five-model ladder",
        "",
        "```mermaid",
        "flowchart LR",
        '    RA["Representative-agent benchmark"] --> RBC["RBC<br/>real benchmark"]',
        '    RA --> PRICE["Price-rigidity RANK core"]',
        f'    PRICE --> CALVO["{names["rank_calvo_sticky_prices"]}"]',
        f'    PRICE --> ROT["{names["rank_rotemberg_sticky_prices"]}"]',
        '    RA --> WAGE["Wage-rigidity RANK core"]',
        f'    WAGE --> MONOPOLY["{names["rank_union_sticky_wages"]}"]',
        f'    WAGE --> MONOPSONY["{names["rank_firm_sticky_wages"]}"]',
        "```",
        "",
        "The overview is a family map. The five detailed figures below are the",
        "code-derived economic DAGs.",
        "",
        "| Model | Blocks | Unknowns -> zero targets | Calibration status |",
        "|---|---|---|---|",
    ]
    for bundle in models.values():
        blocks = ", ".join(f"`{name}`" for name in bundle.block_names)
        contract = (
            ", ".join(f"`{name}`" for name in bundle.unknowns)
            + " -> "
            + ", ".join(f"`{name}`" for name in bundle.targets)
        )
        lines.append(
            f"| **{bundle.display_name}** (`{bundle.name}`) | {blocks} | {contract} | "
            f"`{bundle.calibration_profile.status}` |"
        )
    for bundle in models.values():
        lines.extend(
            [
                "",
                f"## {bundle.display_name}",
                "",
                bundle.description,
                "",
                f"Calibration: `{bundle.calibration_profile.name}` "
                f"(`{bundle.calibration_profile.status}`).",
                "",
                f"![{bundle.display_name} DAG]({bundle.name}.svg)",
            ]
        )
    (directory / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_artifacts(output_directory: str | Path = "figures", horizon: int = 80) -> dict:
    """Build all models, export DAGs, solve IRFs, and return an audit summary."""

    if horizon < 2:
        raise ValueError("horizon must be at least 2")
    output_directory = Path(output_directory)
    dag_directory = output_directory / "dags"
    irf_directory = output_directory / "irfs"
    dag_directory.mkdir(parents=True, exist_ok=True)
    irf_directory.mkdir(parents=True, exist_ok=True)

    models = build_all_models()
    summary: dict[str, dict] = {}
    impulses: dict[str, object] = {}
    for bundle in models.values():
        export_dag(bundle, dag_directory)
        shock_name, shock_path = reference_shock(bundle, horizon)
        impulse = bundle.solve_impulse_linear({shock_name: shock_path})
        impulses[bundle.name] = impulse
        _write_irf_csv(irf_directory / f"{bundle.name}.csv", impulse)
        residuals = {
            target: float(bundle.steady_state[target])
            for target in bundle.targets
        }
        summary[bundle.name] = {
            "display_name": bundle.display_name,
            "description": bundle.description,
            "mechanism_status": bundle.mechanism_status,
            "calibration": {
                "profile": bundle.calibration_profile.name,
                "status": bundle.calibration_profile.status,
                "sources": list(bundle.calibration_profile.sources),
                "notes": list(bundle.calibration_profile.notes),
                "declared_values": {
                    name: float(value)
                    for name, value in bundle.calibration_profile.values.items()
                },
            },
            "cartridge": bundle.cartridge,
            "blocks": list(bundle.block_names),
            "unknowns": list(bundle.unknowns),
            "targets": list(bundle.targets),
            "exogenous": list(bundle.exogenous),
            "steady_state_residuals": residuals,
            "reference_shock": shock_name,
            "reference_shock_impact": float(shock_path[0]),
            "unknown_impacts": {
                unknown: float(impulse[unknown][0])
                for unknown in bundle.unknowns
            },
            "provenance": provenance_rows(bundle.block_names),
        }
    (output_directory / "audit_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_dag_index(dag_directory, models)
    export_output_irf_figures(models, impulses, irf_directory)
    return summary
