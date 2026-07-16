"""Interchangeable price-setting cartridges with identical contracts."""

import sequence_jacobian as sj


@sj.simple
def price_calvo(
    pi_p,
    mc_gap,
    mc_slope,
    beta,
    theta_p,
    alpha,
    epsilon_p,
    psi_p,
):
    """Galí Calvo NKPC, expressed first in the marginal-cost gap.

    ``psi_p`` is deliberately accepted but unused.  Both price cartridges
    expose one exact SSJ contract, including cartridge-specific parameters.
    """

    omega_p = (1 - alpha) / (1 - alpha + alpha * epsilon_p)
    lambda_p = (1 - theta_p) * (1 - beta * theta_p) / theta_p * omega_p
    kappa_p = lambda_p * mc_slope
    price_residual = beta * pi_p(+1) + lambda_p * mc_gap - pi_p
    return omega_p, lambda_p, kappa_p, price_residual


@sj.simple
def price_rotemberg(
    pi_p,
    mc_gap,
    mc_slope,
    beta,
    theta_p,
    alpha,
    epsilon_p,
    psi_p,
):
    """First-order Rotemberg NKPC under the documented cost normalization.

    ``theta_p`` and ``alpha`` are unused cartridge-specific inputs retained so
    this block has exactly the same SSJ interface as ``price_calvo``.
    """

    omega_p = 1.0
    lambda_p = (epsilon_p - 1) / psi_p
    kappa_p = lambda_p * mc_slope
    price_residual = beta * pi_p(+1) + lambda_p * mc_gap - pi_p
    return omega_p, lambda_p, kappa_p, price_residual


PRICE_CARTRIDGES = {
    "calvo": price_calvo,
    "rotemberg": price_rotemberg,
}
