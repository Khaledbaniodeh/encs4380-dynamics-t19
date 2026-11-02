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


def step_curve(k, tau, amplitude=1.0, end_time=None, num_points=101):
    """Return time and output lists for plotting the exact step response.

    By default, sample from t=0 to t=5*tau at 101 equally spaced points.
    end_time can set a fixed observation window in seconds.
    k and amplitude may be positive, negative, or zero.
    Sampling the closed-form solution is not numerical ODE integration.
    """
    # Reuse the single-point function's parameter checks.
    step_response(t=0, k=k, tau=tau, amplitude=amplitude)

    if end_time is None:
        end_time = 5 * tau
    if not isfinite(end_time) or end_time <= 0:
        raise ValueError("end_time must be finite and greater than zero.")
    if isinstance(num_points, bool) or not isinstance(num_points, int):
        raise ValueError("num_points must be an integer.")
    if num_points < 2:
        raise ValueError("num_points must be at least two.")

    times = []
    outputs = []

    for index in range(num_points):
        t = (index / (num_points - 1)) * end_time
        y = step_response(t=t, k=k, tau=tau, amplitude=amplitude)
        times.append(t)
        outputs.append(y)

    return {"time": times, "output": outputs}
