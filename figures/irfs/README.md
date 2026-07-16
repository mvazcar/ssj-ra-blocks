# Output impulse-response comparisons

The three retained figures are the repository's final plotting design:
large Helvetica type, open axes, horizontal guides, MATLAB blue and
red-orange, and solid/dashed encoding for comparisons.

## RBC benchmark

![RBC output response](rbc_output_response.svg)

The shock is a 1% technology innovation with `rho=0.90`.

## Calvo versus Rotemberg prices

![Price-setting comparison](rank_price_output_comparison.svg)

Both models receive the same 25 bp monetary-policy shock. Their
first-order responses coincide because the Rotemberg cost matches the
Calvo Phillips-curve slope.

## Union versus firm wage setting

![Wage-setting comparison](rank_wage_output_comparison.svg)

Both models receive the same 25 bp innovation in the wage-inflation
policy rule. The impact sign reversal is the Dennery mechanism.

## Normalization

- RBC output is `100 * dY / Y_ss` because the model is in levels.
- RANK output is `100 * y` because the models are in log deviations.
- Each model's full-system IRF is stored in its own CSV.

Only the price pair and wage pair are controlled within-family comparisons.
