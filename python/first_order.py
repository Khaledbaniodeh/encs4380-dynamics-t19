"""Closed-form first-order sensor responses for ENCS4380, Team T19."""

from math import exp, expm1, isfinite


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



def step_error_fraction(t, tau):
    """Return E(t) = exp(-t/tau) for a nonzero, zero-initial step.

    This normalized error is meaningful when k * amplitude is nonzero.
    Use the exponential directly to avoid subtracting nearly equal values.
    """
    if not all(isfinite(value) for value in (t, tau)):
        raise ValueError("t and tau must be finite numbers.")
    if tau <= 0:
        raise ValueError("tau must be greater than zero.")
    if t < 0:
        raise ValueError("t must be zero or positive.")
    return exp(-t / tau)


def step_log_error_slope(tau):
    """Return the slope of ln(E(t)) against time, in inverse seconds."""
    if not isfinite(tau) or tau <= 0:
        raise ValueError("tau must be finite and greater than zero.")
    return -1.0 / tau


def ramp_response(t, k, tau, slope=1.0):
    """Return the zero-initial response to x(t) = slope * t.

    Equivalent to k*slope*(t - tau*(1 - exp(-t/tau))).
    expm1(z) computes exp(z)-1 accurately near zero.
    """
    if not all(isfinite(value) for value in (t, k, tau, slope)):
        raise ValueError("All inputs must be finite numbers.")
    if tau <= 0:
        raise ValueError("tau must be greater than zero.")
    if t < 0:
        raise ValueError("t must be zero or positive.")
    return k * slope * (t + tau * expm1(-t / tau))


def ramp_ideal_response(t, k, slope=1.0):
    """Return the instantaneous ideal output k*x(t), where x(t)=slope*t.

    Passing k=1 also gives the raw ramp input x(t).
    """
    if not all(isfinite(value) for value in (t, k, slope)):
        raise ValueError("All inputs must be finite numbers.")
    if t < 0:
        raise ValueError("t must be zero or positive.")
    return k * slope * t
