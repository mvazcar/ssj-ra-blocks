"""Canonical RBC blocks, algebraically matching the official SSJ example."""

import sequence_jacobian as sj


@sj.simple
def rbc_firm(K, L, Z, alpha, delta):
    """Competitive Cobb–Douglas firm; capital chosen at t-1."""

    r = alpha * Z * (K(-1) / L) ** (alpha - 1) - delta
    w = (1 - alpha) * Z * (K(-1) / L) ** alpha
    Y = Z * K(-1) ** alpha * L ** (1 - alpha)
    return r, w, Y


@sj.simple
def rbc_household(K, L, w, sigma, phi, chi, delta):
    """Household block in Galí preference notation.

    ``sigma`` is inverse EIS, ``phi`` is inverse Frisch elasticity, and
    ``chi`` is the labor-disutility weight.
    """

    C = (w / chi / L**phi) ** (1 / sigma)
    I = K - (1 - delta) * K(-1)
    return C, I


@sj.simple
def rbc_markets(r, C, Y, I, K, L, w, sigma, beta):
    """Goods clearing, Euler equation, and a redundant Walras check."""

    goods_mkt = Y - C - I
    euler = C ** (-sigma) - beta * (1 + r(+1)) * C(+1) ** (-sigma)
    walras = C + K - (1 + r) * K(-1) - w * L
    return goods_mkt, euler, walras
