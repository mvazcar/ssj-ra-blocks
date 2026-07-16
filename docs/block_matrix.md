# Block matrix and exchange contracts

This table is the compact map of which named SSJ block appears in each model.
The generated JSON DAGs contain the same information plus every input, output,
parameter, and source record.

| SSJ block | `rbc` | `rank_calvo_sticky_prices` | `rank_rotemberg_sticky_prices` | `rank_union_sticky_wages` | `rank_firm_sticky_wages` |
|---|:---:|:---:|:---:|:---:|:---:|
| `rbc_firm` | yes | | | | |
| `rbc_household` | yes | | | | |
| `rbc_markets` | yes | | | | |
| `natural_allocation` | | yes | yes | | |
| `output_identity` | | yes | yes | | |
| `price_core_diagnostics` | | yes | yes | | |
| `taylor_price` | | yes | yes | | |
| `dynamic_is` | | yes | yes | | |
| `price_calvo` | | yes | | | |
| `price_rotemberg` | | | yes | | |
| `wage_activity` | | | | yes | yes |
| `wage_output` | | | | yes | yes |
| `taylor_wage` | | | | yes | yes |
| `labor_demand_monopoly` | | | | yes | |
| `wage_pc_monopoly` | | | | yes | |
| `labor_supply_monopsony` | | | | | yes |
| `wage_pc_monopsony` | | | | | yes |

## Exact exchange contracts

The functions in each row below have identical SSJ input and output lists.
Mechanism-specific parameters remain visible as inputs even where one of the
two mechanisms does not use them. This is intentional: swapping a cartridge
does not change the surrounding model's wiring.

| Socket | Alternatives | Inputs | Outputs |
|---|---|---|---|
| price setting | `price_calvo`, `price_rotemberg` | `pi_p`, `mc_gap`, `mc_slope`, `beta`, `theta_p`, `alpha`, `epsilon_p`, `psi_p` | `omega_p`, `lambda_p`, `kappa_p`, `price_residual` |
| wage intertemporal closure | `labor_demand_monopoly`, `labor_supply_monopsony` | `l`, `i`, `pi_w`, `r_nat`, `labor_demand_coefficient`, `phi` | `intertemporal_residual` |
| wage Phillips curve | `wage_pc_monopoly`, `wage_pc_monopsony` | `pi_w`, `l`, `activity_coefficient`, `beta`, `theta_w`, `phi`, `epsilon_w`, `alpha`, `eta` | `lambda_w`, `kappa_w`, `wage_residual` |

The two wage rows must be exchanged together. A Phillips-curve-only switch is
not the Dennery model.

The words *monopoly* and *monopsony* refer to the wage setter behind these model
identifiers: workers/unions under monopoly, employers under monopsony. Goods
prices are flexible in both models.
