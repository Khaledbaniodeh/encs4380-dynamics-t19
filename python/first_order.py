"""Closed-form first-order sensor responses for ENCS4380, Team T19."""

from math import exp, expm1, isfinite
import json


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


def ramp_tracking_metrics(t, k, tau, slope=1.0):
    """Return (asymptotic time lag, current signed error, steady-state error).

    Error is measured against the ideal output k*x(t), not the raw input.
    The lag is not meaningful when the ideal output has zero slope.
    """
    if not all(isfinite(value) for value in (t, k, tau, slope)):
        raise ValueError("All inputs must be finite numbers.")
    if tau <= 0:
        raise ValueError("tau must be greater than zero.")
    if t < 0:
        raise ValueError("t must be zero or positive.")

    steady_error = k * slope * tau
    current_error = -steady_error * expm1(-t / tau)
    time_lag = tau if k != 0 and slope != 0 else None
    return time_lag, current_error, steady_error


def step_validation_json(k, tau, amplitude=1.0):
    """Check the lecture's rounded 63.2% and 95% step benchmarks.

    Compare fractions with tolerance 0.0005 (0.05 percentage points),
    allowing for the lecture's rounding. Zero final output has no defined
    percentage. JSON keeps numbers, booleans and None explicit in the UI.
    """
    if not all(isfinite(value) for value in (k, tau, amplitude)):
        raise ValueError("All inputs must be finite numbers.")
    if tau <= 0:
        raise ValueError("tau must be greater than zero.")
    final_output = k * amplitude
    if not isfinite(final_output):
        raise ValueError("Final output is outside the supported numeric range.")

    rows = []
    for multiple, expected_fraction in ((1, 0.632), (3, 0.95)):
        time = multiple * tau
        actual_output = step_response(time, k, tau, amplitude)
        actual_fraction = actual_output / final_output if final_output != 0 else None
        passed = (abs(actual_fraction - expected_fraction) <= 0.0005
                  if actual_fraction is not None else None)
        rows.append({
            "multiple": multiple,
            "time": time,
            "expected_output": expected_fraction * final_output,
            "actual_output": actual_output,
            "expected_percent": 100 * expected_fraction,
            "actual_percent": 100 * actual_fraction if actual_fraction is not None else None,
            "passed": passed,
        })
    return json.dumps(rows, allow_nan=False)


def check_tau_prediction_json(before_tau, after_tau, guess):
    """Check a prediction about increasing tau for a nonzero step.

    The lecture's 63.2% marker is at t=tau, for either output sign.
    """
    if not all(isfinite(value) and value > 0 for value in (before_tau, after_tau)):
        raise ValueError("Time constants must be finite and positive.")
    if after_tau <= before_tau:
        raise ValueError("Increase tau above its saved value before checking.")
    if guess not in ("longer", "shorter", "same"):
        raise ValueError("Choose a prediction first.")
    before_time = before_tau
    after_time = after_tau
    actual = "longer" if after_time > before_time else "shorter" if after_time < before_time else "same"
    return json.dumps({
        "correct": guess == actual,
        "before_time": before_time,
        "after_time": after_time,
        "actual": actual,
    }, allow_nan=False)
