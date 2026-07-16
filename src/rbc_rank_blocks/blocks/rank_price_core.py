"""Shared Galí Chapter 3 RANK blocks for price-rigidity comparisons."""

import sequence_jacobian as sj


@sj.simple
def natural_allocation(a, z, sigma, phi, alpha, rho_a, rho_z):
    """Galí natural output and natural real rate (Chapter 3, eqs. 20 and 24)."""

    psi_n_ya = (1 + phi) / (sigma * (1 - alpha) + phi + alpha)
    y_nat = psi_n_ya * a
    r_nat = -sigma * psi_n_ya * (1 - rho_a) * a + (1 - rho_z) * z
    return psi_n_ya, y_nat, r_nat


@sj.simple
def output_identity(x, y_nat):
    """Observed output equals the output gap plus natural output."""

    y = x + y_nat
    return y


@sj.simple
def price_core_diagnostics(y, y_nat, a, sigma, phi, alpha):
    """Expose the household/firm wedges hidden by the three-equation form.

    Flexible wages imply the real wage equals the MRS. Marginal cost is
    therefore MRS minus MPL in log deviations. The last equality,
    `mc_gap = mc_slope * (y-y_nat)`, is returned as `mc_identity_error` and
    tested numerically.
    """

    c = y
    n = (y - a) / (1 - alpha)
    mrs = sigma * c + phi * n
    mpl = a - alpha * n
    mc_gap = mrs - mpl
    mc_slope = sigma + (phi + alpha) / (1 - alpha)
    mc_identity_error = mc_gap - mc_slope * (y - y_nat)
    return c, n, mrs, mpl, mc_gap, mc_slope, mc_identity_error


@sj.simple
def taylor_price(pi_p, y, nu, phi_pi, phi_y):
    """Galí current-inflation/current-output Taylor rule."""

    i = phi_pi * pi_p + phi_y * y + nu
    return i


@sj.simple
def dynamic_is(x, i, pi_p, r_nat, sigma):
    """Dynamic IS equation; `is_residual=0` is the equilibrium condition."""

    is_residual = x - x(+1) + (i - pi_p(+1) - r_nat) / sigma
    return is_residual
