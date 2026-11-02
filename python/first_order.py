"""Closed-form first-order sensor responses for ENCS4380, Team T19."""

from math import exp, isfinite


def step_response(t, k, tau, amplitude=1.0):
    """Return y(t) for a step from zero to amplitude, with y(0) = 0.

    t and tau use seconds. k is the static gain. The final output is
    k * amplitude. This function computes one point, not a complete plot.
    Only Python's standard library is required.
    """
    if not all(isfinite(value) for value in (t, k, tau, amplitude)):
        raise ValueError("All inputs must be finite numbers.")
    if tau <= 0:
        raise ValueError("tau must be greater than zero.")
    if t < 0:
        raise ValueError("t must be zero or positive.")

    output = k * amplitude * (1 - exp(-t / tau))
    return output
