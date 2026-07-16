"""Minimal, dependency-free SVG output-response figures."""

from __future__ import annotations

import math
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .models import ModelBundle


MATLAB_BLUE = "#0072BD"
MATLAB_ORANGE = "#D95319"
HELVETICA = "Helvetica,Arial,sans-serif"


@dataclass(frozen=True)
class OutputSeries:
    """One output response in percentage deviations."""

    label: str
    values: np.ndarray
    color: str
    dash: str | None = None


def output_response_percent(bundle: ModelBundle, impulse: Mapping[str, Any]) -> np.ndarray:
    """Put level-RBC and log-linear RANK output on a percent scale."""

    if bundle.family == "rbc":
        return 100.0 * np.asarray(impulse["Y"], dtype=float) / float(
            bundle.steady_state["Y"]
        )
    if bundle.family in {"rank_price", "rank_wage"}:
        return 100.0 * np.asarray(impulse["y"], dtype=float)
    raise ValueError(f"Unknown model family {bundle.family!r}")


def _nice_step(raw_step: float) -> float:
    if raw_step <= 0:
        return 1.0
    power = 10.0 ** math.floor(math.log10(raw_step))
    fraction = raw_step / power
    for candidate in (1.0, 2.0, 2.5, 5.0, 10.0):
        if fraction <= candidate:
            return candidate * power
    return 10.0 * power


def _nice_axis(
    values: Sequence[np.ndarray], target_intervals: int = 5
) -> tuple[tuple[float, float], tuple[float, ...]]:
    finite = np.concatenate([np.asarray(value, dtype=float) for value in values])
    finite = finite[np.isfinite(finite)]
    lower = min(float(finite.min()), 0.0)
    upper = max(float(finite.max()), 0.0)
    if math.isclose(lower, upper):
        lower -= 0.5
        upper += 0.5
    padding = 0.06 * (upper - lower)
    lower -= padding if lower < 0 else 0.0
    upper += padding if upper > 0 else 0.0
    step = _nice_step((upper - lower) / target_intervals)
    lower = math.floor(lower / step) * step
    upper = math.ceil(upper / step) * step
    ticks: list[float] = []
    tick = lower
    while tick <= upper + step * 1e-8:
        ticks.append(0.0 if abs(tick) < step * 1e-8 else tick)
        tick += step
    return (lower, upper), tuple(ticks)


def _format_tick(value: float) -> str:
    if math.isclose(value, 0.0):
        return "0.0"
    return f"{value:.1f}"


def _line_path(
    values: np.ndarray,
    x: float,
    y: float,
    width: float,
    height: float,
    y_bounds: tuple[float, float],
    max_period: int,
) -> str:
    lower, upper = y_bounds
    points: list[str] = []
    for period, value in enumerate(np.asarray(values[: max_period + 1], dtype=float)):
        px = x + width * period / max_period
        py = y + height * (upper - float(value)) / (upper - lower)
        points.append(f"{'M' if period == 0 else 'L'} {px:.2f} {py:.2f}")
    return " ".join(points)


def _output_svg(
    series: tuple[OutputSeries, ...],
    description: str,
    max_period: int,
) -> str:
    """Render the repository's single selected Helvetica/MATLAB plot style."""

    y_bounds, y_ticks = _nice_axis(
        [item.values[: max_period + 1] for item in series], target_intervals=5
    )
    lower, upper = y_bounds
    width, height = 900, 675
    plot_x, plot_y, plot_width, plot_height = 132.0, 38.0, 690.0, 520.0
    x_ticks = tuple(round(max_period * share / 4) for share in range(5))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(description)}</title>',
        f'<desc id="desc">{escape(description)}. Output is in percent deviations; '
        "the figure uses Helvetica, open axes, horizontal guides, and MATLAB colors.</desc>",
        '<defs><clipPath id="plot-clip"><rect x="132" y="38" width="690" height="520"/></clipPath></defs>',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
    ]

    for tick in y_ticks:
        py = plot_y + plot_height * (upper - tick) / (upper - lower)
        is_zero = math.isclose(tick, 0.0)
        parts.extend(
            [
                f'<line x1="{plot_x:.1f}" y1="{py:.1f}" '
                f'x2="{plot_x + plot_width:.1f}" y2="{py:.1f}" '
                f'stroke="#000000" stroke-opacity="{0.32 if is_zero else 0.16}" '
                f'stroke-width="{1.9 if is_zero else 1.5}"/>',
                f'<line x1="{plot_x - 8:.1f}" y1="{py:.1f}" x2="{plot_x:.1f}" '
                'y2="{:.1f}" stroke="#000000" stroke-width="1.8"/>'.format(py),
                f'<text x="{plot_x - 17:.1f}" y="{py + 11:.1f}" text-anchor="end" '
                f'font-family="{HELVETICA}" font-size="34" fill="#000000">'
                f"{escape(_format_tick(tick))}</text>",
            ]
        )

    for tick in x_ticks:
        px = plot_x + plot_width * tick / max_period
        parts.extend(
            [
                f'<line x1="{px:.1f}" y1="{plot_y + plot_height:.1f}" '
                f'x2="{px:.1f}" y2="{plot_y + plot_height + 8:.1f}" '
                'stroke="#000000" stroke-width="1.8"/>',
                f'<text x="{px:.1f}" y="{plot_y + plot_height + 48:.1f}" '
                f'text-anchor="middle" font-family="{HELVETICA}" font-size="34" '
                f'fill="#000000">{tick}</text>',
            ]
        )

    for item in series:
        dash = f' stroke-dasharray="{item.dash}"' if item.dash else ""
        parts.append(
            f'<path d="{_line_path(item.values, plot_x, plot_y, plot_width, plot_height, y_bounds, max_period)}" '
            f'fill="none" stroke="{item.color}" stroke-width="5.5" '
            f'stroke-linejoin="round" stroke-linecap="butt"{dash} '
            'clip-path="url(#plot-clip)"/>'
        )

    parts.extend(
        [
            f'<line x1="{plot_x:.1f}" y1="{plot_y:.1f}" x2="{plot_x:.1f}" '
            f'y2="{plot_y + plot_height:.1f}" stroke="#000000" stroke-width="1.8"/>',
            f'<line x1="{plot_x:.1f}" y1="{plot_y + plot_height:.1f}" '
            f'x2="{plot_x + plot_width:.1f}" y2="{plot_y + plot_height:.1f}" '
            'stroke="#000000" stroke-width="1.8"/>',
        ]
    )

    legend_x = plot_x + plot_width - (max(len(item.label) for item in series) * 16 + 120)
    legend_y = plot_y + plot_height * 0.62 if upper <= 0 else plot_y + 55
    for index, item in enumerate(series):
        y = legend_y + index * 52
        dash = f' stroke-dasharray="{item.dash}"' if item.dash else ""
        parts.extend(
            [
                f'<line x1="{legend_x:.1f}" y1="{y:.1f}" x2="{legend_x + 72:.1f}" '
                f'y2="{y:.1f}" stroke="{item.color}" stroke-width="5.5"{dash}/>',
                f'<text x="{legend_x + 92:.1f}" y="{y + 11:.1f}" '
                f'font-family="{HELVETICA}" font-size="31" fill="#000000">'
                f"{escape(item.label)}</text>",
            ]
        )

    parts.extend(
        [
            f'<text x="{plot_x + plot_width / 2:.1f}" y="654" text-anchor="middle" '
            f'font-family="{HELVETICA}" font-size="38" fill="#000000">Quarter</text>',
            f'<text x="42" y="{plot_y + plot_height / 2:.1f}" '
            f'transform="rotate(-90 42 {plot_y + plot_height / 2:.1f})" '
            f'text-anchor="middle" font-family="{HELVETICA}" font-size="38" '
            'fill="#000000">% change in output</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def _write_index(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# Output impulse-response comparisons",
                "",
                "The three retained figures are the repository's final plotting design:",
                "large Helvetica type, open axes, horizontal guides, MATLAB blue and",
                "red-orange, and solid/dashed encoding for comparisons.",
                "",
                "## RBC benchmark",
                "",
                "![RBC output response](rbc_output_response.svg)",
                "",
                "The shock is a 1% technology innovation with `rho=0.90`.",
                "",
                "## Calvo versus Rotemberg prices",
                "",
                "![Price-setting comparison](rank_price_output_comparison.svg)",
                "",
                "Both models receive the same 25 bp monetary-policy shock. Their",
                "first-order responses coincide because the Rotemberg cost matches the",
                "Calvo Phillips-curve slope.",
                "",
                "## Union versus firm wage setting",
                "",
                "![Wage-setting comparison](rank_wage_output_comparison.svg)",
                "",
                "Both models receive the same 25 bp innovation in the wage-inflation",
                "policy rule. The impact sign reversal is the Dennery mechanism.",
                "",
                "## Normalization",
                "",
                "- RBC output is `100 * dY / Y_ss` because the model is in levels.",
                "- RANK output is `100 * y` because the models are in log deviations.",
                "- Each model's full-system IRF is stored in its own CSV.",
                "",
                "Only the price pair and wage pair are controlled within-family comparisons.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def export_output_irf_figures(
    models: Mapping[str, ModelBundle],
    impulses: Mapping[str, Mapping[str, Any]],
    directory: str | Path,
    max_period: int = 20,
) -> dict[str, Path]:
    """Write the three final comparison SVGs and their short index."""

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    response = {
        name: output_response_percent(bundle, impulses[name])
        for name, bundle in models.items()
    }
    max_period = min(max_period, *(len(values) - 1 for values in response.values()))
    if max_period < 1:
        raise ValueError("At least two IRF periods are required for a figure")

    figures = {
        "rbc": (
            directory / "rbc_output_response.svg",
            (OutputSeries("RBC", response["rbc"], MATLAB_BLUE),),
            "RBC output response to a technology shock",
        ),
        "price": (
            directory / "rank_price_output_comparison.svg",
            (
                OutputSeries(
                    "Calvo prices", response["rank_calvo_sticky_prices"], MATLAB_BLUE
                ),
                OutputSeries(
                    "Rotemberg prices",
                    response["rank_rotemberg_sticky_prices"],
                    MATLAB_ORANGE,
                    "9 6",
                ),
            ),
            "RANK output under Calvo and Rotemberg sticky prices",
        ),
        "wage": (
            directory / "rank_wage_output_comparison.svg",
            (
                OutputSeries(
                    "Union wages", response["rank_union_sticky_wages"], MATLAB_BLUE
                ),
                OutputSeries(
                    "Firm wages",
                    response["rank_firm_sticky_wages"],
                    MATLAB_ORANGE,
                    "9 6",
                ),
            ),
            "RANK output under union- and firm-set sticky wages",
        ),
    }
    paths: dict[str, Path] = {}
    for name, (path, series, description) in figures.items():
        path.write_text(_output_svg(series, description, max_period), encoding="utf-8")
        paths[name] = path
    paths["index"] = directory / "README.md"
    _write_index(paths["index"])
    return paths
