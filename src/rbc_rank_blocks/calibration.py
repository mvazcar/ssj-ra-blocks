"""Reference calibrations, source labels, and explicit slope mappings.

Dennery (2020) identifies the monopsony mechanism but does not provide a
unique quantitative calibration.  The audit metadata therefore labels that
profile as empirically anchored rather than canonical.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


SSJ_RBC_URL = (
    "https://github.com/shade-econ/sequence-jacobian/blob/"
    "eb4ac4c3157357a4cacbea4b5a7a281f5b48cab9/notebooks/rbc.ipynb"
)
GALI_CH3_URL = "https://crei.cat/wp-content/uploads/users/pages/ch3_slides_june2015%281%29.pdf"
PFEIFER_GALI_URL = (
    "https://github.com/JohannesPfeifer/DSGE_mod/blob/"
    "26c21f79e4c6a6b19b18e6330edc5b23489907a4/Gali_2015/"
    "Gali_2015_chapter_3.mod"
)
ROTEMBERG_URL = "https://academic.oup.com/restud/article/49/4/517/1538719"
EHL_URL = "https://www.federalreserve.gov/pubs/ifdp/1999/640/ifdp640.pdf"
DENNERY_URL = (
    "https://infoscience.epfl.ch/server/api/core/bitstreams/"
    "95d0c174-e80a-4162-bf83-aed446713d25/content"
)
BHM_URL = "https://www.aeaweb.org/articles?id=10.1257%2Faer.20191521"


@dataclass(frozen=True)
class CalibrationProfile:
    """Numerical values plus an explicit statement of their authority."""

    name: str
    status: str
    values: Mapping[str, float]
    sources: tuple[str, ...]
    notes: tuple[str, ...]


def rbc_calibration() -> dict[str, float]:
    """Calibration used by the official SSJ RBC example.

    The equations are canonical; these numerical values are the upstream
    teaching normalization and are kept so this implementation can be
    regression tested against the official example.
    """

    return {
        "sigma": 1.0,
        "phi": 1.0,
        "delta": 0.025,
        "alpha": 0.11,
        "L": 1.0,
    }


def rbc_profile() -> CalibrationProfile:
    return CalibrationProfile(
        name="official-ssj-rbc-reproduction",
        status="source-reproduction",
        values=rbc_calibration(),
        sources=(SSJ_RBC_URL,),
        notes=(
            "Equations and numerical normalization reproduce the official SSJ RBC notebook.",
            "Galí notation: sigma is inverse EIS and phi is inverse Frisch.",
            "alpha=0.11 is the notebook normalization, not a universal RBC calibration.",
        ),
    )


def rank_price_calibration() -> dict[str, float]:
    """Galí (2015), Chapter 3 quarterly baseline calibration.

    ``psi_p`` is the Rotemberg adjustment cost that matches the Calvo
    marginal-cost slope at this same calibration.
    """

    calibration = {
        # Preferences and technology
        "beta": 0.99,
        "sigma": 1.0,
        "phi": 5.0,
        "alpha": 0.25,
        # Product demand and nominal rigidity
        "epsilon_p": 9.0,
        "theta_p": 0.75,
        # Policy and shock persistence used in the natural allocation
        "phi_pi": 1.5,
        "phi_y": 0.125,
        "rho_a": 0.9,
        "rho_z": 0.5,
        # Zero-deviation steady state
        "a": 0.0,
        "z": 0.0,
        "nu": 0.0,
        "x": 0.0,
        "pi_p": 0.0,
    }
    calibration["psi_p"] = matched_rotemberg_cost(calibration)
    return calibration


def rank_price_profile(setting: str) -> CalibrationProfile:
    if setting not in {"calvo", "rotemberg"}:
        raise ValueError(f"Unknown price-setting profile {setting!r}")
    mechanism_note = (
        "Calvo probability and the remaining values are Galí's Chapter 3 baseline."
        if setting == "calvo"
        else "The Rotemberg cost is derived to match Galí's Calvo slope at first order."
    )
    return CalibrationProfile(
        name=f"gali-chapter-3-{setting}",
        status=(
            "canonical-textbook-calibration"
            if setting == "calvo"
            else "standard-mechanism-matched-normalization"
        ),
        values=rank_price_calibration(),
        sources=(
            (GALI_CH3_URL, PFEIFER_GALI_URL)
            if setting == "calvo"
            else (ROTEMBERG_URL, GALI_CH3_URL, PFEIFER_GALI_URL)
        ),
        notes=(
            mechanism_note,
            "The Rotemberg and Calvo models share every parameter except "
            "the price-setting normalization.",
        ),
    )


def calvo_marginal_cost_slope(calibration: Mapping[str, float]) -> float:
    """Return the coefficient multiplying the marginal-cost gap under Calvo."""

    beta = calibration["beta"]
    theta = calibration["theta_p"]
    alpha = calibration["alpha"]
    epsilon = calibration["epsilon_p"]
    omega = (1.0 - alpha) / (1.0 - alpha + alpha * epsilon)
    return (1.0 - theta) * (1.0 - beta * theta) / theta * omega


def matched_rotemberg_cost(calibration: Mapping[str, float]) -> float:
    """Choose Rotemberg adjustment cost so its first-order slope equals Calvo's.

    With the normalization documented in ``docs/equations.md``, Rotemberg's
    marginal-cost coefficient is ``(epsilon_p - 1) / psi_p``.
    """

    return (calibration["epsilon_p"] - 1.0) / calvo_marginal_cost_slope(calibration)


def _rank_wage_common_calibration() -> dict[str, float]:
    """EHL quarterly structural values used for the clean wage comparison."""

    return {
        # EHL quarterly structural benchmark
        "beta": 0.99,
        "sigma": 1.5,
        "phi": 1.5,
        "alpha": 0.30,
        "theta_w": 0.75,
        # A one-third wage markup implies epsilon_w=4.
        "epsilon_w": 4.0,
        # eta=4 implies eta/(eta+1)=0.8, close to BHM's 0.78 markdown.
        "eta": 4.0,
        # Transparent comparison closure; not supplied numerically by Dennery.
        "phi_w": 1.5,
        "phi_y_w": 0.0,
        # Exogenous sequences and zero-deviation steady state
        "r_nat": 0.0,
        "nu_w": 0.0,
        "l": 0.0,
        "pi_w": 0.0,
    }


def rank_monopoly_calibration() -> dict[str, float]:
    """EHL structural benchmark specialized to flexible goods prices."""

    return _rank_wage_common_calibration()


def rank_monopsony_calibration() -> dict[str, float]:
    """Dennery mechanism in the common EHL environment with eta=4."""

    return _rank_wage_common_calibration()


def rank_wage_profile(setter: str) -> CalibrationProfile:
    if setter == "monopoly":
        return CalibrationProfile(
            name="ehl-sticky-wage-flexible-price",
            status="canonical-foundation-with-explicit-policy-closure",
            values=rank_monopoly_calibration(),
            sources=(EHL_URL, DENNERY_URL),
            notes=(
                "beta, sigma, phi, alpha, theta_w, and the one-third wage "
                "markup follow EHL's quarterly benchmark.",
                "Flexible goods prices select EHL's sticky-wage special case "
                "used in Dennery's comparison.",
                "phi_w=1.5 is a conventional determinate comparison closure, "
                "not an EHL or Dennery estimate.",
            ),
        )
    if setter == "monopsony":
        return CalibrationProfile(
            name="dennery-monopsony-eta4",
            status="source-mechanism-empirically-anchored-calibration",
            values=rank_monopsony_calibration(),
            sources=(DENNERY_URL, EHL_URL, BHM_URL),
            notes=(
                "Dennery supplies the Phillips-curve sign and labor-supply "
                "closure but no unique numerical calibration.",
                "The common EHL environment isolates the change in wage setter.",
                "eta=4 implies a 0.8 markdown, close to "
                "Berger-Herkenhoff-Mongey's payroll-weighted 0.78 benchmark.",
                "phi_w=1.5 is a conventional determinate comparison closure, "
                "not a source estimate.",
            ),
        )
    raise ValueError(f"Unknown wage-setting profile {setter!r}")
