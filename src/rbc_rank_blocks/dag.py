"""Export auditable DAGs directly from assembled SSJ model objects.

The SVG and Mermaid files are views of the same JSON specification.  Edges
are inferred from each live block's ``inputs`` and ``outputs`` attributes, so
the pictures cannot silently drift away from the code.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import Any

from .models import ModelBundle
from .provenance import BLOCK_SOURCES


MATLAB_BLUE = "#0072BD"
MATLAB_ORANGE = "#D95319"

# The DAGs share the plot language: white canvas, Helvetica, neutral structure,
# and MATLAB blue/orange only for economically distinct boundary objects.
KIND_STYLE = {
    "unknown": ("#EAF4FA", MATLAB_BLUE),
    "shock": ("#FCEFE8", MATLAB_ORANGE),
    "block": ("#FFFFFF", "#000000"),
    "target": ("#F2F2F2", "#000000"),
}

# Inputs retained only to make cartridges exactly exchangeable.  Recording them
# here prevents the live-interface DAG from overstating an economic dependency.
INTERFACE_ONLY_INPUTS = {
    "price_calvo": {"psi_p"},
    "price_rotemberg": {"theta_p", "alpha"},
    "labor_demand_monopoly": {"phi"},
    "labor_supply_monopsony": {"labor_demand_coefficient"},
    "wage_pc_monopoly": {"alpha", "eta"},
    "wage_pc_monopsony": {"phi", "epsilon_w"},
}

VARIABLE_LABELS = {
    "K": "Capital (K)",
    "L": "Labor (L)",
    "Z": "Productivity (Z)",
    "x": "Output gap (x)",
    "pi_p": "Price inflation (pi_p)",
    "l": "Labor gap (l)",
    "pi_w": "Wage inflation (pi_w)",
}

VARIABLE_SYMBOLS = {
    "pi_p": "pi_p",
    "pi_w": "pi_w",
    "y_nat": "y*",
    "r_nat": "r*",
    "goods_mkt": "goods residual",
    "euler": "Euler residual",
    "is_residual": "IS residual",
    "price_residual": "price residual",
    "intertemporal_residual": "intertemporal residual",
    "wage_residual": "wage residual",
}

BLOCK_LABELS = {
    "rbc_firm": "Production",
    "rbc_household": "Household",
    "rbc_markets": "Market clearing",
    "natural_allocation": "Natural allocation",
    "output_identity": "Output",
    "taylor_price": "Policy rule",
    "dynamic_is": "Dynamic IS",
    "price_core_diagnostics": "Price diagnostics",
    "price_calvo": "Calvo prices",
    "price_rotemberg": "Rotemberg prices",
    "wage_output": "Output",
    "taylor_wage": "Wage policy rule",
    "wage_activity": "Wage activity",
    "labor_demand_monopoly": "Labor demand",
    "wage_pc_monopoly": "Union wage curve",
    "labor_supply_monopsony": "Labor supply",
    "wage_pc_monopsony": "Firm wage curve",
}

TARGET_LABELS = {
    "goods_mkt": "Goods market",
    "euler": "Euler equation",
    "is_residual": "IS equilibrium",
    "price_residual": "Price equilibrium",
    "intertemporal_residual": "Intertemporal equilibrium",
    "wage_residual": "Wage equilibrium",
}


def _safe_id(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value)


def _variable_label(value: str) -> str:
    return VARIABLE_LABELS.get(value, value)


def _variable_symbol(value: str) -> str:
    return VARIABLE_SYMBOLS.get(value, value)


def _block_label(value: str) -> str:
    return BLOCK_LABELS.get(value, value.replace("_", " ").title())


def _target_label(value: str) -> str:
    return TARGET_LABELS.get(value, value.replace("_", " ").title())


def _steady_scalar(bundle: ModelBundle, name: str) -> float | None:
    """Return a JSON-safe steady-state scalar when the live model contains it."""

    try:
        return float(bundle.steady_state[name])
    except (KeyError, TypeError, ValueError):
        return None


def dag_spec(bundle: ModelBundle) -> dict[str, Any]:
    """Return a serializable specification inferred from one live SSJ model."""

    blocks = list(bundle.model.blocks)
    producers = {
        output: block.name
        for block in blocks
        for output in block.outputs
    }
    unknowns = set(bundle.unknowns)
    exogenous = set(bundle.exogenous)

    nodes: list[dict[str, Any]] = []
    for variable in bundle.unknowns:
        nodes.append(
            {
                "id": f"unknown:{variable}",
                "label": _variable_label(variable),
                "kind": "unknown",
                "subtitle": "GE unknown",
                "level": 0,
            }
        )
    for variable in bundle.exogenous:
        nodes.append(
            {
                "id": f"shock:{variable}",
                "label": _variable_label(variable),
                "kind": "shock",
                "subtitle": "exogenous sequence",
                "level": 0,
            }
        )

    block_levels: dict[str, int] = {}
    block_rows: list[dict[str, Any]] = []
    for block in blocks:
        parent_levels = [
            block_levels[producers[variable]]
            for variable in block.inputs
            if variable in producers and producers[variable] in block_levels
        ]
        level = 1 + max(parent_levels, default=0)
        block_levels[block.name] = level
        parameter_inputs = [
            variable
            for variable in block.inputs
            if variable not in producers
            and variable not in unknowns
            and variable not in exogenous
        ]
        parameter_values = {
            variable: value
            for variable in parameter_inputs
            if (value := _steady_scalar(bundle, variable)) is not None
        }
        source = BLOCK_SOURCES.get(block.name)
        row = {
            "name": block.name,
            "inputs": list(block.inputs),
            "outputs": list(block.outputs),
            "parameters": parameter_inputs,
            "parameter_values": parameter_values,
            "interface_only_inputs": sorted(INTERFACE_ONLY_INPUTS.get(block.name, set())),
            "source": asdict(source) if source is not None else None,
        }
        block_rows.append(row)
        nodes.append(
            {
                "id": f"block:{block.name}",
                "label": _block_label(block.name),
                "kind": "block",
                "subtitle": "outputs "
                + ", ".join(_variable_symbol(value) for value in block.outputs),
                "code_name": block.name,
                "level": level,
            }
        )

    max_block_level = max(block_levels.values(), default=0)
    for target in bundle.targets:
        producer = producers.get(target)
        level = block_levels.get(producer, max_block_level) + 1
        nodes.append(
            {
                "id": f"target:{target}",
                "label": _target_label(target),
                "kind": "target",
                "subtitle": "zero target",
                "code_name": target,
                "level": level,
            }
        )

    edge_variables: dict[tuple[str, str, bool], list[str]] = defaultdict(list)
    for block in blocks:
        destination = f"block:{block.name}"
        for variable in block.inputs:
            if variable in producers:
                source = f"block:{producers[variable]}"
            elif variable in unknowns:
                source = f"unknown:{variable}"
            elif variable in exogenous:
                source = f"shock:{variable}"
            else:
                continue
            interface_only = variable in INTERFACE_ONLY_INPUTS.get(block.name, set())
            edge_variables[(source, destination, interface_only)].append(variable)

    for target in bundle.targets:
        if target in producers:
            edge_variables[
                (f"block:{producers[target]}", f"target:{target}", False)
            ].append(target)

    edges = [
        {
            "from": source,
            "to": destination,
            "variables": variables,
            "interface_only": interface_only,
        }
        for (source, destination, interface_only), variables in edge_variables.items()
    ]
    all_parameter_names = sorted(
        {parameter for row in block_rows for parameter in row["parameters"]}
    )
    live_parameter_values = {
        name: value
        for name in all_parameter_names
        if (value := _steady_scalar(bundle, name)) is not None
    }
    profile = bundle.calibration_profile
    return {
        "model": bundle.name,
        "display_name": bundle.display_name,
        "family": bundle.family,
        "description": bundle.description,
        "mechanism_status": bundle.mechanism_status,
        "calibration": {
            "profile": profile.name,
            "status": profile.status,
            "sources": list(profile.sources),
            "notes": list(profile.notes),
            "declared_values": {
                name: float(value) for name, value in profile.values.items()
            },
            "live_parameter_values": live_parameter_values,
        },
        "cartridge": bundle.cartridge,
        "solution": {
            "unknowns": list(bundle.unknowns),
            "targets": list(bundle.targets),
            "exogenous": list(bundle.exogenous),
        },
        "blocks": block_rows,
        "nodes": nodes,
        "edges": edges,
        "note": (
            "Calibration parameters and values are listed per block in JSON and omitted from visual arrows. "
            "Dashed edges are socket-only inputs retained for exact exchangeability."
        ),
    }


def to_mermaid(spec: dict[str, Any]) -> str:
    """Render one DAG specification as portable Mermaid source."""

    lines = ["flowchart LR"]
    for node in spec["nodes"]:
        identifier = _safe_id(node["id"])
        label = node["label"].replace('"', "'")
        subtitle = node["subtitle"].replace('"', "'")
        if node["kind"] == "block":
            lines.append(f'    {identifier}["{label}<br/><small>{subtitle}</small>"]')
        elif node["kind"] == "target":
            lines.append(f'    {identifier}{{"{label}<br/><small>{subtitle}</small>"}}')
        else:
            lines.append(f'    {identifier}(["{label}<br/><small>{subtitle}</small>"])')
    for edge in spec["edges"]:
        source = _safe_id(edge["from"])
        destination = _safe_id(edge["to"])
        variables = ", ".join(edge["variables"])
        connector = "-.->" if edge["interface_only"] else "-->"
        suffix = " (socket only)" if edge["interface_only"] else ""
        lines.append(f"    {source} {connector}|{variables}{suffix}| {destination}")
    lines.extend(
        [
            "    classDef unknown fill:#EAF4FA,stroke:#0072BD,color:#000000;",
            "    classDef shock fill:#FCEFE8,stroke:#D95319,color:#000000;",
            "    classDef block fill:#FFFFFF,stroke:#000000,color:#000000;",
            "    classDef target fill:#F2F2F2,stroke:#000000,color:#000000;",
        ]
    )
    for kind in KIND_STYLE:
        ids = ",".join(
            _safe_id(node["id"])
            for node in spec["nodes"]
            if node["kind"] == kind
        )
        if ids:
            lines.append(f"    class {ids} {kind};")
    return "\n".join(lines) + "\n"


def _shorten(value: str, length: int = 52) -> str:
    return value if len(value) <= length else value[: length - 1] + "…"


def to_svg(spec: dict[str, Any]) -> str:
    """Render a dependency-free, readable SVG for one DAG specification."""

    node_width = 250
    node_height = 72
    x_gap = 120
    y_gap = 34
    margin_x = 55
    top = 145
    bottom = 85

    by_level: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for node in spec["nodes"]:
        by_level[int(node["level"])].append(node)
    levels = sorted(by_level)
    max_rows = max((len(by_level[level]) for level in levels), default=1)
    width = 2 * margin_x + len(levels) * node_width + max(0, len(levels) - 1) * x_gap
    content_height = max_rows * node_height + max(0, max_rows - 1) * y_gap
    height = top + content_height + bottom

    positions: dict[str, tuple[float, float]] = {}
    for column, level in enumerate(levels):
        column_nodes = by_level[level]
        column_height = len(column_nodes) * node_height + max(0, len(column_nodes) - 1) * y_gap
        offset = top + (content_height - column_height) / 2
        x = margin_x + column * (node_width + x_gap)
        for row, node in enumerate(column_nodes):
            y = offset + row * (node_height + y_gap)
            positions[node["id"]] = (x, y)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<defs>",
        '<marker id="arrow" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto"><polygon points="0 0, 9 3.5, 0 7" fill="#64748b"/></marker>',
        '<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.12"/></filter>',
        "</defs>",
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        f'<text x="{margin_x}" y="42" font-family="Helvetica,Arial,sans-serif" font-size="25" font-weight="700" fill="#0f172a">{escape(spec["display_name"])}</text>',
        f'<text x="{margin_x}" y="69" font-family="Helvetica,Arial,sans-serif" font-size="14" fill="#475569">{escape(_shorten(spec["description"], 150))}</text>',
        f'<text x="{margin_x}" y="96" font-family="Helvetica,Arial,sans-serif" font-size="12" fill="#64748b">Generated from live SSJ inputs/outputs · mechanism: {escape(spec["mechanism_status"])}</text>',
    ]

    legend_x = margin_x
    for kind, label in (
        ("unknown", "GE unknown"),
        ("shock", "exogenous"),
        ("block", "SSJ block"),
        ("target", "zero target"),
    ):
        fill, stroke = KIND_STYLE[kind]
        parts.append(
            f'<rect x="{legend_x}" y="112" width="16" height="12" rx="3" fill="{fill}" stroke="{stroke}"/>'
        )
        parts.append(
            f'<text x="{legend_x + 22}" y="123" font-family="Helvetica,Arial,sans-serif" font-size="11" fill="#475569">{label}</text>'
        )
        legend_x += 105

    # Draw connectors behind nodes. A curved path remains readable when rows differ.
    for edge in spec["edges"]:
        x1, y1 = positions[edge["from"]]
        x2, y2 = positions[edge["to"]]
        start_x = x1 + node_width
        start_y = y1 + node_height / 2
        end_x = x2 - 7
        end_y = y2 + node_height / 2
        bend = max(35, (end_x - start_x) * 0.42)
        dash = ' stroke-dasharray="7 5"' if edge["interface_only"] else ""
        parts.append(
            f'<path d="M {start_x:.1f} {start_y:.1f} C {start_x + bend:.1f} {start_y:.1f}, {end_x - bend:.1f} {end_y:.1f}, {end_x:.1f} {end_y:.1f}" fill="none" stroke="#64748b" stroke-width="1.5"{dash} marker-end="url(#arrow)"/>'
        )
        label_x = (start_x + end_x) / 2
        label_y = (start_y + end_y) / 2 - 5
        suffix = " (socket)" if edge["interface_only"] else ""
        label = _shorten(", ".join(edge["variables"]) + suffix, 34)
        text_width = max(30, len(label) * 6.3 + 10)
        parts.append(
            f'<rect x="{label_x - text_width / 2:.1f}" y="{label_y - 12:.1f}" width="{text_width:.1f}" height="17" rx="4" fill="#f8fafc" fill-opacity="0.94"/>'
        )
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="10.5" fill="#334155">{escape(label)}</text>'
        )

    for node in spec["nodes"]:
        x, y = positions[node["id"]]
        fill, stroke = KIND_STYLE[node["kind"]]
        radius = 18 if node["kind"] in {"unknown", "shock"} else 10
        code_name = node.get("code_name", node["id"].split(":", 1)[-1])
        parts.append(
            f'<g id="{_safe_id(node["id"])}" data-node-id="{escape(node["id"])}" '
            f'data-code-name="{escape(code_name)}">'
        )
        parts.append(
            f'<rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.8" filter="url(#shadow)"/>'
        )
        parts.append(
            f'<text x="{x + 14}" y="{y + 29}" font-family="Helvetica,Arial,sans-serif" font-size="14" font-weight="700" fill="#0f172a">{escape(_shorten(node["label"], 32))}</text>'
        )
        parts.append(
            f'<text x="{x + 14}" y="{y + 51}" font-family="Helvetica,Arial,sans-serif" font-size="10.5" fill="#475569">{escape(_shorten(node["subtitle"]))}</text>'
        )
        parts.append("</g>")

    parts.append(
        f'<text x="{margin_x}" y="{height - 28}" font-family="Helvetica,Arial,sans-serif" font-size="11" fill="#64748b">Parameters are in the companion JSON; dashed edges are interface-only inputs retained for exact cartridge exchangeability.</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def export_dag(bundle: ModelBundle, directory: str | Path) -> dict[str, Path]:
    """Write synchronized JSON, Mermaid, and SVG views for one model."""

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    spec = dag_spec(bundle)
    paths = {
        "json": directory / f"{bundle.name}.json",
        "mermaid": directory / f"{bundle.name}.mmd",
        "svg": directory / f"{bundle.name}.svg",
    }
    paths["json"].write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    paths["mermaid"].write_text(to_mermaid(spec), encoding="utf-8")
    paths["svg"].write_text(to_svg(spec), encoding="utf-8")
    return paths
