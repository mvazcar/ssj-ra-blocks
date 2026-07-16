# Sources and authority

The files under `sources/upstream/` were downloaded before implementation.
They are intentionally ignored by Git because they include nested repositories,
archives, and third-party licensing. `sources/manifest.json` pins everything
needed to fetch and verify the same material.

## Source hierarchy

| Question | Source of truth | Local material |
|---|---|---|
| How should an SSJ RBC be divided into blocks? | Official `shade-econ/sequence-jacobian` RBC example and notebook | `sources/upstream/sequence-jacobian/` |
| What is the canonical basic price-sticky RANK? | Galí, *Monetary Policy, Inflation, and the Business Cycle*, Chapter 3 | Galí slides and TeX source under `sources/upstream/downloaded/` and `extracted/` |
| What executable equations reproduce Galí Chapter 3? | Johannes Pfeifer's maintained Dynare implementations | `sources/upstream/DSGE_mod/Gali_2015/` |
| What is the preferred SSJ composition style for RA/TA/HA comparisons? | Auclert–Rognlie–Straub Annual Review code | `sources/upstream/annual-review/` |
| What is the worker/union sticky-wage foundation and calibration? | Erceg–Henderson–Levin (2000), flexible-price special case | `sources/upstream/downloaded/ehl_1999_ifdp640.pdf` |
| What changes under employer wage setting? | Dennery (2020), equations (7), (9), and footnote 13 | `sources/upstream/downloaded/dennery_2020.pdf` |
| What is a transparent empirical anchor for `eta`? | Berger–Herkenhoff–Mongey (2022) | AEA article and replication-package links recorded in `docs/calibration.md` |

## Important distinction

Pfeifer's Dynare files are a maintained independent implementation, not code
published by Galí. Galí's own site supplies the Chapter 3 slides and their TeX
source. We use Galí for model definition and Pfeifer as the executable oracle.

The Annual Review repository is authoritative for SSJ architecture and model
composition. It is not used to redefine the canonical Galí equations.

The official SSJ test suite also contains a model explicitly named `RANK` in
`tests/base/test_workflow.py`. It is an important architectural cross-check for
the representative-household + union composition, but its calibration is a
software-test fixture rather than a canonical quantitative benchmark.

EHL supplies a genuine quarterly structural calibration for worker/union wage
setting: `beta=0.99`, household utility curvatures of `1.5`, `alpha=0.3`,
one-third wage and price markup rates, and four-quarter average contracts. The
repository uses the sticky-wage/flexible-price special case.

Dennery supplies the monopsony mechanism, including the negative wage Phillips
curve and the replacement of intertemporal labor demand by labor supply. The
paper explicitly states that its qualitative comparison does not depend on a
specific calibration; it does not publish a unique numerical benchmark. The
default `eta=4` is therefore labeled empirically anchored rather than canonical.
