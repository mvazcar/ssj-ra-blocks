"""Equation-level provenance attached to each named SSJ block."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BlockSource:
    block: str
    role: str
    equation: str
    source: str
    url: str
    status: str = "direct"


SSJ_RBC_URL = (
    "https://github.com/shade-econ/sequence-jacobian/blob/"
    "eb4ac4c3157357a4cacbea4b5a7a281f5b48cab9/notebooks/rbc.ipynb"
)
GALI_MOD_URL = (
    "https://github.com/JohannesPfeifer/DSGE_mod/blob/"
    "26c21f79e4c6a6b19b18e6330edc5b23489907a4/Gali_2015/"
    "Gali_2015_chapter_3.mod"
)
GALI_NONLINEAR_URL = (
    "https://github.com/JohannesPfeifer/DSGE_mod/blob/"
    "26c21f79e4c6a6b19b18e6330edc5b23489907a4/Gali_2015/"
    "Gali_2015_chapter_3_nonlinear.mod"
)
DENNERY_URL = (
    "https://infoscience.epfl.ch/server/api/core/bitstreams/"
    "95d0c174-e80a-4162-bf83-aed446713d25/content"
)


BLOCK_SOURCES = {
    "rbc_firm": BlockSource(
        "rbc_firm",
        "production and factor prices",
        "official SSJ RBC firm block",
        "Auclert et al. sequence-jacobian example",
        SSJ_RBC_URL,
    ),
    "rbc_household": BlockSource(
        "rbc_household",
        "labor supply and capital accumulation",
        "official SSJ RBC household block",
        "Auclert et al. sequence-jacobian example",
        SSJ_RBC_URL,
    ),
    "rbc_markets": BlockSource(
        "rbc_markets",
        "Euler equation and clearing",
        "official SSJ RBC market block",
        "Auclert et al. sequence-jacobian example",
        SSJ_RBC_URL,
    ),
    "natural_allocation": BlockSource(
        "natural_allocation",
        "natural output and real rate",
        "Galí Chapter 3 equations (20), (24)",
        "Galí (2015), checked against Pfeifer's Dynare file",
        GALI_MOD_URL,
    ),
    "output_identity": BlockSource(
        "output_identity",
        "output-gap definition",
        "x_t = y_t - y_t^n",
        "Galí (2015), Chapter 3",
        "https://crei.cat/people/gali/",
        "algebraic-identity",
    ),
    "price_core_diagnostics": BlockSource(
        "price_core_diagnostics",
        "labor, MRS, MPL, and marginal-cost diagnostics",
        "Galí Chapter 3 equations (11), (12), and marginal-cost identity",
        "Galí (2015), expanded from the canonical three-equation model",
        GALI_MOD_URL,
        "algebraic-expansion",
    ),
    "dynamic_is": BlockSource(
        "dynamic_is",
        "representative-household Euler equation",
        "Galí Chapter 3 equation (23)",
        "Galí (2015), checked against Pfeifer's Dynare file",
        GALI_MOD_URL,
    ),
    "taylor_price": BlockSource(
        "taylor_price",
        "price-inflation Taylor rule",
        "Galí Chapter 3 equation (26)",
        "Galí (2015), checked against Pfeifer's Dynare file",
        GALI_MOD_URL,
    ),
    "price_calvo": BlockSource(
        "price_calvo",
        "Calvo New Keynesian Phillips curve",
        "Galí Chapter 3 equation (22)",
        "Galí (2015), nonlinear structure checked against Pfeifer",
        GALI_NONLINEAR_URL,
    ),
    "price_rotemberg": BlockSource(
        "price_rotemberg",
        "Rotemberg New Keynesian Phillips curve",
        "first-order PC under quadratic price adjustment",
        "Rotemberg (1982); SSJ normalization documented locally",
        "https://academic.oup.com/restud/article/49/4/517/1538719",
        "derived-normalization",
    ),
    "wage_activity": BlockSource(
        "wage_activity",
        "reduced-form activity gap and slopes",
        "Dennery footnote 13 definitions",
        "Dennery (2020)",
        DENNERY_URL,
        "algebraic-identity",
    ),
    "wage_output": BlockSource(
        "wage_output",
        "labor-to-output mapping",
        "log-linear production y_t=(1-alpha)l_t",
        "Dennery (2020), Cobb-Douglas specialization used in footnote 13",
        DENNERY_URL,
        "algebraic-identity",
    ),
    "taylor_wage": BlockSource(
        "taylor_wage",
        "wage-inflation Taylor rule",
        "Dennery section 2.3 and footnote 12",
        "Dennery (2020)",
        DENNERY_URL,
    ),
    "labor_demand_monopoly": BlockSource(
        "labor_demand_monopoly",
        "intertemporal labor demand",
        "Dennery equation (8), footnote 13",
        "EHL wage-monopoly comparison as written by Dennery (2020)",
        DENNERY_URL,
    ),
    "wage_pc_monopoly": BlockSource(
        "wage_pc_monopoly",
        "worker/union wage Phillips curve",
        "Dennery footnote 9 and footnote 13",
        "Erceg–Henderson–Levin (2000) comparison",
        "https://www.federalreserve.gov/pubs/ifdp/1999/640/ifdp640.pdf",
    ),
    "labor_supply_monopsony": BlockSource(
        "labor_supply_monopsony",
        "intertemporal labor supply",
        "Dennery equation (9)",
        "Dennery (2020)",
        DENNERY_URL,
    ),
    "wage_pc_monopsony": BlockSource(
        "wage_pc_monopsony",
        "employer wage Phillips curve",
        "Dennery equation (7), footnote 13",
        "Dennery (2020)",
        DENNERY_URL,
    ),
}


def provenance_rows(block_names: list[str] | tuple[str, ...]) -> list[dict[str, str]]:
    """Return serializable provenance rows for blocks that have direct sources."""

    return [asdict(BLOCK_SOURCES[name]) for name in block_names if name in BLOCK_SOURCES]
