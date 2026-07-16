# Calibration authority

This repository separates three questions that are often conflated:

1. Is the **mechanism** canonical or directly source-derived?
2. Is the **numerical calibration** copied from that source?
3. Is a value a transparent normalization introduced only for comparison?

Every generated DAG JSON records the profile name, status, sources, notes,
declared values, and the final parameter values in the live SSJ model.

## Profiles

| Model | Profile | Status | Main caveat |
|---|---|---|---|
| `rbc` | `official-ssj-rbc-reproduction` | source reproduction | The official notebook uses `alpha=0.11`; this is a teaching normalization, not a universal RBC calibration |
| `rank_calvo_sticky_prices` | `gali-chapter-3-calvo` | canonical textbook calibration | Direct quarterly Galí Chapter 3 baseline |
| `rank_rotemberg_sticky_prices` | `gali-chapter-3-rotemberg` | standard mechanism, matched normalization | `psi_p` is derived so the first-order Phillips slope equals the Calvo slope |
| `rank_union_sticky_wages` | `ehl-sticky-wage-flexible-price` | canonical foundation with explicit policy closure | Structural values follow EHL; `phi_w=1.5` is a conventional determinate closure |
| `rank_firm_sticky_wages` | `dennery-monopsony-eta4` | source mechanism, empirically anchored calibration | Dennery gives no unique numerical calibration; `eta=4` is an explicit empirical anchor |

## RBC

The default is copied from the official SSJ RBC notebook:

| Parameter | Value |
|---|---:|
| Inverse EIS `sigma` | 1 |
| Inverse Frisch elasticity `phi` | 1 |
| Depreciation `delta` | 0.025 |
| Capital share `alpha` | 0.11 |
| Steady labor `L` | 1 |

The model then solves jointly for `chi`, `beta`, `K`, and `Z` to impose
`Y=1`, `r=0.01`, goods clearing, and the Euler equation. This is an exact
source-reproduction profile. Galí-style notation is used across the ladder:
`sigma` is inverse EIS, `phi` is inverse Frisch elasticity, and `chi` is the
labor-disutility weight. Thus EIS is `1/sigma` and the Frisch elasticity is
`1/phi`.

## Price-rigidity RANK

Both price models use the Galí Chapter 3 quarterly baseline:

| Parameter | Value | Interpretation |
|---|---:|---|
| `beta` | 0.99 | Discount factor |
| `sigma` | 1 | Inverse EIS |
| `phi` | 5 | Inverse Frisch elasticity |
| `alpha` | 0.25 | Decreasing-returns/labor technology parameter |
| `epsilon_p` | 9 | Goods demand elasticity |
| `theta_p` | 0.75 | Probability of not resetting price |
| `phi_pi` | 1.5 | Taylor response to price inflation |
| `phi_y` | 0.125 | Taylor response to output |
| `rho_a` | 0.9 | Technology persistence |
| `rho_z` | 0.5 | Preference-shock persistence |

For Rotemberg pricing, `psi_p` is not copied from Galí. It is only the
price-adjustment cost and is unrelated to household preference curvature. It
is computed from

\[
\frac{\epsilon_p-1}{\psi_p}
=
\frac{(1-\theta_p)(1-\beta\theta_p)}{\theta_p}
\frac{1-\alpha}{1-\alpha+\alpha\epsilon_p}.
\]

Consequently, `rank_calvo_sticky_prices` and `rank_rotemberg_sticky_prices` have identical first-order
IRFs at the default profile. They differ beyond first order and when `psi_p` is
moved away from the matched value.

## Wage-rigidity RANK

The common structural environment uses the quarterly EHL benchmark:

| Parameter | Value | Authority |
|---|---:|---|
| `beta` | 0.99 | EHL |
| `sigma` | 1.5 | EHL household utility |
| `phi` | 1.5 | Inverse Frisch elasticity in the EHL household utility |
| `alpha` | 0.30 | EHL capital-share/technology parameter |
| `theta_w` | 0.75 | EHL four-quarter average wage contract |
| `epsilon_w` | 4 | Implied by EHL's one-third wage markup |
| `phi_w` | 1.5 | Explicit comparison convention |
| `phi_y_w` | 0 | Explicit comparison convention |

The monopoly model uses the EHL worker/union wage Phillips curve in the
flexible-goods-price special case. Dennery uses precisely this case as the
comparison against employer wage setting.

The monopsony model keeps the same common environment and changes both the
Phillips curve and the intertemporal condition. Its `eta=4` implies the simple
markdown `eta/(eta+1)=0.8`. Berger, Herkenhoff, and Mongey (2022) report a
payroll-weighted average labor-supply elasticity below five and a markdown near
0.78, so `eta=4` is a transparent empirical anchor. It is **not** a value
estimated or calibrated by Dennery.

## What was taken from shade-econ

- The official `sequence-jacobian` RBC notebook is the direct source for the
  RBC block structure and numerical reproduction.
- `sequence-jacobian/tests/base/test_workflow.py` contains an SSJ model named
  `RANK`, built from a representative household, firm, union, fiscal, and market
  blocks. In this repository's notation its software-test fixture has
  `sigma=2` (`EIS=0.5`), `nu=0.5`, `kappaw=0.1`, and `muw=1.2`, so those
  values are not used as a canonical calibration.
- The shade-econ Annual Review code is the authority for transparent RA/TA/HA
  composition. Its quarterly union NKPC uses a reduced-form `kappa=0.01` inside
  a richer fiscal/asset-market model. That is a valuable alternative profile,
  but it is not silently substituted into the structural EHL/Dennery cartridge.

## Primary sources

- [Official SSJ repository](https://github.com/shade-econ/sequence-jacobian)
- [Galí Chapter 3 materials](https://crei.cat/people/gali/)
- [Pfeifer's executable Galí Chapter 3 implementation](https://github.com/JohannesPfeifer/DSGE_mod/tree/master/Gali_2015)
- [EHL Federal Reserve paper](https://www.federalreserve.gov/pubs/ifdp/1999/640/ifdp640.pdf)
- [Dennery (2020)](https://infoscience.epfl.ch/server/api/core/bitstreams/95d0c174-e80a-4162-bf83-aed446713d25/content)
- [Berger, Herkenhoff, and Mongey (2022)](https://www.aeaweb.org/articles?id=10.1257%2Faer.20191521)
