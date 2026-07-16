# Adversarial verification

This document records what was checked, what the checks establish, and what
they do not establish. The goal is auditability rather than an unqualified
claim that a model is “perfect.”

## Source chain

The local source tree was checked against the tracked manifest:

| Source | Pinned revision or integrity check | Role |
|---|---|---|
| `shade-econ/sequence-jacobian` | `eb4ac4c3157357a4cacbea4b5a7a281f5b48cab9` | Exact RBC blocks and SSJ behavior |
| `shade-econ/annual-review` | `80ef0c1ef5e739aa8cec3b57e14304a3ece958b5` | Independent SSJ composition cross-check |
| `JohannesPfeifer/DSGE_mod` | `26c21f79e4c6a6b19b18e6330edc5b23489907a4` | Executable Galí Chapter 3 cross-check |
| Galí, EHL, and Dennery files | SHA-256 values in `sources/manifest.json` | Primary equations and independent checks |

`scripts/fetch_sources.ps1` downloads and checks the material.
`scripts/verify_sources.ps1` performs the integrity check again without
changing the source tree.

## Equation audit

### RBC

The three functions in `blocks/rbc.py` were compared line by line with the
pinned official SSJ RBC notebook. Production, factor prices, household labor
supply, capital accumulation, goods clearing, the Euler equation, and the
Walras check use the same equations. The steady-state solve uses the same
normalization and targets. The only intentional notation change uses the same
preference names across the full ladder: `sigma` is inverse EIS, `phi` is
inverse Frisch elasticity, and `chi` is the labor-disutility weight. This
translation does not change the benchmark solution.

The notation was checked directly against Galí's Chapter 3 slide 9: utility
has consumption curvature `sigma` and labor curvature `phi`, the intratemporal
condition is `w-p = sigma*c + phi*n`, and the dynamic IS coefficient is
`1/sigma`. Thus `sigma` is inverse EIS and `phi` is inverse Frisch.

### Price-rigidity RANK

The natural-output coefficient, natural real rate, dynamic IS equation,
Phillips curve, and Taylor rule were checked against Galí Chapter 3 and the
pinned Dynare implementation. One potentially easy mistake was checked
explicitly: the policy rule responds to total output deviation `y=x+y_nat`, as
in the Dynare variable `yhat`, rather than to the output gap `x` alone.

The expanded marginal-cost block was checked algebraically:

\[
\widehat{mc}_t
=\widehat{mrs}_t-\widehat{mpl}_t
=\left[\sigma+\frac{\phi+\alpha}{1-\alpha}\right](y_t-y_t^n).
\]

The Rotemberg block uses a stated quadratic-cost normalization. Its adjustment
cost is derived so that its first-order marginal-cost coefficient equals the
Calvo coefficient. This makes the two blocks first-order equivalent at the
reference profile; it does not claim nonlinear equivalence.

### Wage-rigidity RANK

The EHL calibration was checked on the source parameterization pages: quarterly
`beta=0.99`, utility curvatures of `1.5`, `alpha=0.3`, one-third wage and price
markups, and four-quarter average contracts (`theta_w=0.75`). A one-third wage
markup implies `epsilon_w=4` under the repository’s elasticity notation.

Dennery equations (7), (8), and (9), together with footnote 13, were checked
against the source PDF. The audit confirmed all three features that distinguish
the two wage cartridges:

1. the union Phillips slope is positive;
2. the employer Phillips slope is negative with denominator `1+alpha*eta`;
3. intertemporal labor demand is replaced by intertemporal labor supply.

The wage-inflation policy coefficient and the monopsony elasticity are clearly
marked as comparison choices. They are not attributed to EHL or Dennery.

## Numerical stress checks

The following results were obtained from the live SSJ models before being
encoded as regression tests:

| Check | Result |
|---|---:|
| Largest absolute steady-state target residual | `1.11e-16` |
| Largest marginal-cost identity error across price shocks | `1.39e-17` |
| Calvo versus matched-Rotemberg difference under the `a`, `z`, and `nu` source shocks | `0.0` |
| Error when doubling each reference shock and comparing with twice the response | `0.0` |
| Non-finite values across every live response series | `0` |
| Largest relative change in the first 20 RBC unknown responses when horizon rises from 80 to 160 | `8.05e-7` |
| Largest corresponding RANK change | `2.47e-16` |

The tests also enforce identical SSJ input/output sockets, the documented wage
slope formulas, the Dennery impact-sign reversal, synchronized DAG views,
pinned source links, safe manifest filenames, and the absence of installable
package metadata.

## Repository-design audit

The intended workflow is deliberately narrow:

- `run_models.py` is the single root entry point;
- dependencies are installed from requirements files;
- `pytest.ini` configures test discovery and the internal import path only;
- the internal namespace re-exports no model constructors;
- there is no package `__main__`, build backend, distribution record, or
  editable-install instruction.

The modules under `src/rbc_rank_blocks/` exist only to keep the equations,
assembly, plotting, and provenance readable. They are not presented as a
stable external API.

## Scope limits

- All RANK comparisons are first-order, log-linear solutions.
- Calvo and Rotemberg equivalence is intentionally local to the matched
  first-order slope.
- The sticky-wage models use flexible goods prices. A joint sticky-price and
  sticky-wage model is outside this five-model ladder.
- `eta=4` is an empirical anchor, not a Dennery estimate.
- The simple wage-inflation rule is a transparent determinate closure, not an
  estimated optimal-policy rule.
- TANK and HANK are not included; the repository stays focused on the RA
  foundations and exact block exchanges.

## Reproduce the audit

```powershell
.\.venv\Scripts\python run_models.py
.\.venv\Scripts\python -m pytest
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_sources.ps1
```

The generated `figures/audit_summary.json` records the live block order,
solution contract, calibration status, source rows, steady-state residuals, and
reference-shock impacts for every model.
