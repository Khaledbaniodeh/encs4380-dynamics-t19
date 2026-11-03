"""Exact first-order responses and Forward Euler comparison for ENCS4380 T19."""

from math import ceil, exp, expm1, isfinite
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


def forward_euler(rhs, y0, end_time, dt, max_steps=2000):
    """Integrate a scalar ODE y'=rhs(t,y) using our own Forward Euler loop.

    Both the derivative and increment use the old state. The final step
    is shortened if needed to finish exactly at end_time.
    """
    if not all(isfinite(value) for value in (y0, end_time, dt)):
        raise ValueError("Euler inputs must be finite numbers.")
    if dt <= 0:
        raise ValueError("Euler step Δt must be greater than zero.")
    if end_time < 0:
        raise ValueError("Euler end time must be zero or positive.")
    count = end_time / dt
    if not isfinite(count) or count > max_steps:
        raise ValueError("Euler is limited to 2000 steps. Increase Δt.")
    times, values = [0.0], [float(y0)]
    for index in range(1, ceil(count) + 1):
        old_time, old_y = times[-1], values[-1]
        next_time = min(index * dt, end_time)
        step = next_time - old_time
        if step <= 0:
            continue
        slope = rhs(old_time, old_y)
        next_y = old_y + step * slope
        if not isfinite(slope) or not isfinite(next_y):
            raise ValueError("Euler exceeded the numeric range. Reduce Δt or signal size.")
        times.append(next_time)
        values.append(next_y)
    return times, values


def euler_comparison(mode, k, tau, signal_level, dt):
    """Compare Forward Euler with the exact Module 1 response at Euler nodes.

    signal_level means Step amplitude A or Ramp slope r.
    Absolute errors use output units, including for zero/negative signals.
    Stability describes the homogeneous Euler update, not accuracy.
    """
    if mode not in ("step", "ramp"):
        raise ValueError("Choose Step or Ramp for the Euler comparison.")
    if not all(isfinite(value) for value in (k, tau, signal_level, dt)):
        raise ValueError("Euler needs finite K, τ, signal level and Δt.")
    if tau <= 0:
        raise ValueError("τ must be greater than zero.")
    end_time = 5 * tau
    if not isfinite(end_time):
        raise ValueError("The 0–5τ window exceeds the numeric range.")

    def rhs(time, output):
        input_value = signal_level if mode == "step" else signal_level * time
        return (k * input_value - output) / tau

    times, values = forward_euler(rhs, 0.0, end_time, dt)
    exact_response = step_response if mode == "step" else ramp_response
    exact = [exact_response(time, k, tau, signal_level) for time in times]
    errors = [abs(approx - reference) for approx, reference in zip(values, exact)]
    if not all(isfinite(value) for value in exact + errors):
        raise ValueError("Euler comparison exceeds the numeric range.")
    largest_step_ratio = min(dt, end_time) / tau
    if largest_step_ratio < 2:
        stability = "stable"
        message = "Stable step size. A smaller Δt usually reduces the approximation error."
        if largest_step_ratio > 1:
            stability = "coarse"
            message = "Stable but coarse: numerical oscillations can appear. Stability does not guarantee accuracy."
    elif largest_step_ratio == 2:
        stability = "boundary"
        message = "At the Euler stability boundary: errors need not decay. Reduce Δt."
    else:
        stability = "unstable"
        message = "Outside the Euler stability limit. Oscillations can come from the solver, even when the sensor is stable."
    return {
        "times": times, "values": values, "exact": exact, "errors": errors,
        "max_abs_error": max(errors), "final_abs_error": errors[-1],
        "steps": len(times) - 1, "stability": stability, "message": message,
        "largest_step_ratio": largest_step_ratio,
    }


def euler_comparison_json(mode, k, tau, signal_level, dt):
    """Return a concise result/error for the optional browser comparison."""
    try:
        return json.dumps({"ok": True, **euler_comparison(mode, k, tau, signal_level, dt)},
                          allow_nan=False)
    except (ValueError, OverflowError) as error:
        return json.dumps({"ok": False, "message": str(error)})
