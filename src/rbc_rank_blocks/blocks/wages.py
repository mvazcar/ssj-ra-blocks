"""Worker-monopoly and employer-monopsony wage cartridges.

Each cartridge is a two-block bundle because the identity of the wage setter
changes both the wage Phillips curve and the intertemporal equilibrium curve.
"""

import sequence_jacobian as sj


@sj.simple
def labor_demand_monopoly(
    l,
    i,
    pi_w,
    r_nat,
    labor_demand_coefficient,
    phi,
):
    """Intertemporal labor demand in the worker/union monopoly model.

    ``phi`` is unused but keeps the closure interface exchangeable with
    ``labor_supply_monopsony``.
    """

    intertemporal_residual = (
        labor_demand_coefficient * (l - l(+1))
        + i
        - pi_w(+1)
        - r_nat
    )
    return intertemporal_residual


@sj.simple
def wage_pc_monopoly(
    pi_w,
    l,
    activity_coefficient,
    beta,
    theta_w,
    phi,
    epsilon_w,
    alpha,
    eta,
):
    """EHL worker/union Calvo wage Phillips curve with a positive slope.

    ``alpha`` and ``eta`` are unused but preserve the common PC contract.
    """

    calvo_w = (1 - beta * theta_w) * (1 - theta_w) / theta_w
    lambda_w = calvo_w / (1 + phi * epsilon_w)
    kappa_w = lambda_w * activity_coefficient
    wage_residual = beta * pi_w(+1) + kappa_w * l - pi_w
    return lambda_w, kappa_w, wage_residual


@sj.simple
def labor_supply_monopsony(
    l,
    i,
    pi_w,
    r_nat,
    labor_demand_coefficient,
    phi,
):
    """Dennery equation (9): intertemporal labor supply.

    ``labor_demand_coefficient`` is unused but preserves the common closure
    contract.
    """

    intertemporal_residual = phi * (l - l(+1)) - (
        i - pi_w(+1) - r_nat
    )
    return intertemporal_residual


@sj.simple
def wage_pc_monopsony(
    pi_w,
    l,
    activity_coefficient,
    beta,
    theta_w,
    phi,
    epsilon_w,
    alpha,
    eta,
):
    """Dennery equation (7): employer Calvo wage PC with negative slope.

    ``phi`` and ``epsilon_w`` are unused but preserve the common PC
    contract.
    """

    calvo_w = (1 - beta * theta_w) * (1 - theta_w) / theta_w
    lambda_w = calvo_w / (1 + alpha * eta)
    kappa_w = -lambda_w * activity_coefficient
    wage_residual = beta * pi_w(+1) + kappa_w * l - pi_w
    return lambda_w, kappa_w, wage_residual


WAGE_CARTRIDGES = {
    "monopoly": (labor_demand_monopoly, wage_pc_monopoly),
    "monopsony": (labor_supply_monopsony, wage_pc_monopsony),
}
