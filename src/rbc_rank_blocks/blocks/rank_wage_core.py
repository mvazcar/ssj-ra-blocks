"""Shared quantities for the flexible-goods-price sticky-wage comparison."""

import sequence_jacobian as sj


@sj.simple
def wage_activity(l, sigma, phi, alpha):
    """Activity gap and coefficients appearing in Dennery footnote 13."""

    activity_coefficient = sigma * (1 - alpha) + phi + alpha
    activity_gap = activity_coefficient * l
    labor_demand_coefficient = sigma * (1 - alpha) + alpha
    return activity_coefficient, activity_gap, labor_demand_coefficient


@sj.simple
def wage_output(l, alpha):
    """Translate the labor gap into the output gap for Y=L^(1-alpha)."""

    y = (1 - alpha) * l
    return y


@sj.simple
def taylor_wage(pi_w, y, nu_w, phi_w, phi_y_w):
    """Dennery's wage-inflation rule with footnote 12's output response."""

    i = phi_w * pi_w + phi_y_w * y + nu_w
    return i
