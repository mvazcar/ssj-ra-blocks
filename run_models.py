"""Run the complete RA-SSJ Blocks teaching repository.

This file is the intended entry point.  The modules under ``src/`` are an
internal implementation detail, not an installable or supported package API.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from rbc_rank_blocks.workflow import build_artifacts  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build the five-model RBC/RANK ladder, export live SSJ DAGs, "
            "and solve the documented impulse responses."
        )
    )
    parser.add_argument(
        "--output",
        default="figures",
        help="artifact directory, relative to this repository (default: figures)",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=80,
        help="impulse-response horizon; must be at least 2 (default: 80)",
    )
    arguments = parser.parse_args()

    output = Path(arguments.output)
    if not output.is_absolute():
        output = REPOSITORY_ROOT / output

    summary = build_artifacts(output, arguments.horizon)
    for name, row in summary.items():
        blocks = " -> ".join(row["blocks"])
        impacts = ", ".join(
            f"{variable}={value:+.6g}"
            for variable, value in row["unknown_impacts"].items()
        )
        print(f"{row['display_name']} ({name}): {blocks}")
        print(
            "  calibration: "
            f"{row['calibration']['profile']} [{row['calibration']['status']}]"
        )
        print(f"  {row['reference_shock']} shock impacts: {impacts}")
    print(f"DAGs, audit data, and IRFs written to {output}")


if __name__ == "__main__":
    main()
