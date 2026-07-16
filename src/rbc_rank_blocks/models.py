"""Model registry: the only place where economic blocks are assembled.

Keeping assembly here makes the comparison auditable.  A model is a small
ordered list of named SSJ blocks plus its unknowns, equilibrium targets, and
exogenous sequences.  No equation is hidden in the registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import sequence_jacobian as sj

from .blocks import (
    PRICE_CARTRIDGES,
    WAGE_CARTRIDGES,
    dynamic_is,
    natural_allocation,
    output_identity,
    price_core_diagnostics,
    rbc_firm,
    rbc_household,
    rbc_markets,
    taylor_price,
    taylor_wage,
    wage_activity,
    wage_output,
)
from .calibration import (
    CalibrationProfile,
    rank_price_profile,
    rank_wage_profile,
    rbc_profile,
)


@dataclass(frozen=True)
class ModelBundle:
    """A runnable SSJ model together with its explicit solution contract."""

    name: str
    display_name: str
    family: str
    model: Any
    steady_state: Any
    unknowns: tuple[str, ...]
    targets: tuple[str, ...]
    exogenous: tuple[str, ...]
    description: str
    mechanism_status: str
    calibration_profile: CalibrationProfile
    cartridge: str | None = None

    @property
    def block_names(self) -> tuple[str, ...]:
        """Names in the topological order actually used by SSJ."""

        return tuple(block.name for block in self.model.blocks)

    def solve_impulse_linear(
        self,
        shocks: Mapping[str, Sequence[float]],
        outputs: Sequence[str] | None = None,
    ):
        """Solve one linear impulse response using this bundle's contract."""

        return self.model.solve_impulse_linear(
            self.steady_state,
            list(self.unknowns),
            list(self.targets),
            dict(shocks),
            outputs=None if outputs is None else list(outputs),
        )


def build_rbc() -> ModelBundle:
    """Build the official SSJ representative-agent RBC benchmark."""

    profile = rbc_profile()
    model = sj.create_model(
        [rbc_household, rbc_firm, rbc_markets],
        name="rbc",
    )
    steady_state = model.solve_steady_state(
        dict(profile.values),
        unknowns={"chi": 0.92, "beta": 1 / 1.01, "K": 2.0, "Z": 1.0},
        targets={"goods_mkt": 0.0, "r": 0.01, "euler": 0.0, "Y": 1.0},
        solver="hybr",
    )
    return ModelBundle(
        name="rbc",
        display_name="RBC",
        family="rbc",
        model=model,
        steady_state=steady_state,
        unknowns=("K", "L"),
        targets=("goods_mkt", "euler"),
        exogenous=("Z",),
        description="Canonical competitive RBC model from the official SSJ example.",
        mechanism_status="canonical-equations-source-reproduction",
        calibration_profile=profile,
    )


def build_rank_price(setting: str = "calvo") -> ModelBundle:
    """Build Galí Chapter 3 RANK with a Calvo or Rotemberg price cartridge."""

    try:
        price_block = PRICE_CARTRIDGES[setting]
    except KeyError as exc:
        choices = ", ".join(sorted(PRICE_CARTRIDGES))
        raise ValueError(f"Unknown price cartridge {setting!r}; choose {choices}") from exc

    name = f"rank_{setting}_sticky_prices"
    profile = rank_price_profile(setting)
    model = sj.create_model(
        [
            natural_allocation,
            output_identity,
            price_core_diagnostics,
            taylor_price,
            dynamic_is,
            price_block,
        ],
        name=name,
    )
    steady_state = model.steady_state(dict(profile.values))
    status = (
        "canonical-gali-chapter-3"
        if setting == "calvo"
        else "standard-rotemberg-mechanism-first-order-matched"
    )
    return ModelBundle(
        name=name,
        display_name=f"RANK - {setting.capitalize()} sticky prices",
        family="rank_price",
        model=model,
        steady_state=steady_state,
        unknowns=("x", "pi_p"),
        targets=("is_residual", "price_residual"),
        exogenous=("a", "z", "nu"),
        description=(
            "Galí Chapter 3 representative-agent NK core with "
            f"{setting.capitalize()} price setting and flexible wages."
        ),
        mechanism_status=status,
        calibration_profile=profile,
        cartridge=setting,
    )


def build_rank_wage(setter: str = "monopoly") -> ModelBundle:
    """Build Dennery's flexible-price sticky-wage comparison model."""

    try:
        wage_blocks = WAGE_CARTRIDGES[setter]
    except KeyError as exc:
        choices = ", ".join(sorted(WAGE_CARTRIDGES))
        raise ValueError(f"Unknown wage cartridge {setter!r}; choose {choices}") from exc

    display_setter = "union" if setter == "monopoly" else "firm"
    name = f"rank_{display_setter}_sticky_wages"
    profile = rank_wage_profile(setter)
    model = sj.create_model(
        [wage_activity, wage_output, taylor_wage, *wage_blocks],
        name=name,
    )
    steady_state = model.steady_state(dict(profile.values))
    status = (
        "canonical-ehl-sticky-wage-special-case"
        if setter == "monopoly"
        else "direct-dennery-mechanism"
    )
    wage_setter_description = (
        "wages set by workers/unions (labor monopoly)"
        if setter == "monopoly"
        else "wages set by firms (labor monopsony)"
    )
    return ModelBundle(
        name=name,
        display_name=f"RANK - {display_setter.capitalize()} sticky wages",
        family="rank_wage",
        model=model,
        steady_state=steady_state,
        unknowns=("l", "pi_w"),
        targets=("intertemporal_residual", "wage_residual"),
        exogenous=("r_nat", "nu_w"),
        description=(
            "Flexible-goods-price RANK benchmark with sticky "
            f"{wage_setter_description}, as compared by Dennery (2020)."
        ),
        mechanism_status=status,
        calibration_profile=profile,
        cartridge=setter,
    )


MODEL_NAMES = (
    "rbc",
    "rank_calvo_sticky_prices",
    "rank_rotemberg_sticky_prices",
    "rank_union_sticky_wages",
    "rank_firm_sticky_wages",
)

def build_model(name: str) -> ModelBundle:
    """Build one of the five documented repository models."""

    if name == "rbc":
        return build_rbc()
    if name == "rank_calvo_sticky_prices":
        return build_rank_price("calvo")
    if name == "rank_rotemberg_sticky_prices":
        return build_rank_price("rotemberg")
    if name == "rank_union_sticky_wages":
        return build_rank_wage("monopoly")
    if name == "rank_firm_sticky_wages":
        return build_rank_wage("monopsony")
    choices = ", ".join(MODEL_NAMES)
    raise ValueError(f"Unknown model {name!r}; choose {choices}")


def build_all_models() -> dict[str, ModelBundle]:
    """Build the complete ladder in its documented order."""

    return {name: build_model(name) for name in MODEL_NAMES}
