"""First-order frequency response for ENCS4380 Dynamic Characteristics, Team T19.

The plots use the steady-state response of a stable first-order sensor:
    tau * dy/dt + y = x
    G(s) = 1 / (tau*s + 1)

The module uses unit gain K=1 and unit input amplitude A=1 so that the
frequency-dependent amplitude ratio M can be compared directly to the input.
All frequency inputs named omega are angular frequencies in rad/s.
"""

from math import atan, cos, hypot, isfinite, log10, pi, sin, sqrt
import json


def require_positive(**values):
    """Reject invalid numbers before using them in divisions or logarithms."""
    for name, value in values.items():
        if not isfinite(value) or value <= 0:
            raise ValueError(name + " must be a finite number greater than zero.")


def amplitude_ratio(omega, tau):
    """M = 1 / sqrt(1 + (omega*tau)^2), relative to the static gain."""
    require_positive(omega=omega, tau=tau)
    return 1.0 / hypot(1.0, omega * tau)


def phase_lag_degrees(omega, tau):
    """Negative phase shift in degrees: phi = -atan(omega*tau)."""
    require_positive(omega=omega, tau=tau)
    return -atan(omega * tau) * 180.0 / pi


def cutoff_frequency(tau):
    """First-order cutoff angular frequency, omega_c = 1/tau (rad/s)."""
    require_positive(tau=tau)
    return 1.0 / tau


def dynamic_error_percent(omega, tau):
    """Signed amplitude error percentage: 100*(M-1), not phase error."""
    return 100.0 * (amplitude_ratio(omega, tau) - 1.0)


def maximum_time_constant(max_frequency_hz, max_error_percent):
    """Largest tau satisfying |M-1| <= max_error_percent/100 at max f.

    Hertz is converted to angular frequency with omega = 2*pi*f.
    For a first-order low-pass sensor, magnitude decreases as f increases,
    so checking the highest required frequency covers all lower ones.
    """
    require_positive(max_frequency_hz=max_frequency_hz,
                     max_error_percent=max_error_percent)
    if max_error_percent >= 100:
        raise ValueError("The allowed error must be below 100%.")
    minimum_ratio = 1.0 - max_error_percent / 100.0
    omega_max = 2.0 * pi * max_frequency_hz
    return sqrt(1.0 / (minimum_ratio * minimum_ratio) - 1.0) / omega_max


def dashboard_json(tau, omega):
    """Return all live sine/Bode plotting data in one JSON object.

    The sine output is STEADY STATE: M*sin(omega*t + phi).
    It is not the transient response when a sine is first switched on.
    Bode frequencies are logarithmically spaced around omega_c and omega.
    """
    require_positive(tau=tau, omega=omega)
    ratio = amplitude_ratio(omega, tau)
    phase = -atan(omega * tau)
    cutoff = cutoff_frequency(tau)

    # Three input cycles, including each endpoint, at a fixed sample count.
    duration = 3.0 * (2.0 * pi / omega)
    time = [duration * i / 240 for i in range(241)]
    input_sine = [sin(omega * t) for t in time]
    output_sine = [ratio * sin(omega * t + phase) for t in time]

    # Logarithmic x-axis: 161 positive omega values spaced in log10 space.
    minimum = min(cutoff / 100.0, omega / 10.0)
    maximum = max(cutoff * 100.0, omega * 10.0)
    low_log, high_log = log10(minimum), log10(maximum)
    frequencies = [10 ** (low_log + (high_log - low_log) * i / 160)
                   for i in range(161)]
    magnitudes = [20.0 * log10(amplitude_ratio(w, tau))
                  for w in frequencies]
    phases = [phase_lag_degrees(w, tau) for w in frequencies]

    result = {
        "tau": tau,
        "omega": omega,
        "amplitude_ratio": ratio,
        "output_amplitude": ratio,
        "phase_degrees": phase * 180.0 / pi,
        "time_lag_seconds": -phase / omega,
        "dynamic_error_percent": (ratio - 1.0) * 100.0,
        "cutoff_rad_s": cutoff,
        "cutoff_hz": cutoff / (2.0 * pi),
        "selected_magnitude_db": 20.0 * log10(ratio),
        "time": time,
        "input": input_sine,
        "output": output_sine,
        "bode_omega": frequencies,
        "bode_db": magnitudes,
        "bode_phase": phases,
    }
    return json.dumps(result, allow_nan=False)


def calculator_json(tau, max_frequency_hz, allowed_error_percent):
    """Design calculator comparing the current tau with its allowed limit."""
    require_positive(tau=tau)
    tau_limit = maximum_time_constant(max_frequency_hz,
                                      allowed_error_percent)
    omega_max = 2.0 * pi * max_frequency_hz
    current_error = dynamic_error_percent(omega_max, tau)
    return json.dumps({
        "max_frequency_hz": max_frequency_hz,
        "allowed_error_percent": allowed_error_percent,
        "tau_limit_seconds": tau_limit,
        "tau_limit_ms": 1000.0 * tau_limit,
        "phase_at_half_frequency_deg":
            abs(phase_lag_degrees(omega_max / 2.0, tau_limit)),
        "current_tau_ms": 1000.0 * tau,
        "current_error_percent": current_error,
        "meets_requirement": abs(current_error) <= allowed_error_percent + 1e-10,
    }, allow_nan=False)


def validation_json():
    """Course checks 2 and 3 with displayed rounded lecture benchmarks."""
    ratio = amplitude_ratio(2.0, 0.2)
    phase = abs(phase_lag_degrees(2.0, 0.2))
    tau_ms = 1000.0 * maximum_time_constant(100.0, 5.0)
    half_phase = abs(phase_lag_degrees(2.0 * pi * 50.0,
                          tau_ms / 1000.0))

    checks = [
        {"test": "2 · Amplitude ratio", "expected": 0.93, "actual": ratio,
         "unit": "", "tolerance": 0.01},
        {"test": "2 · Phase lag", "expected": 21.8, "actual": phase,
         "unit": "°", "tolerance": 0.2},
        {"test": "3 · Maximum tau", "expected": 0.52, "actual": tau_ms,
         "unit": "ms", "tolerance": 0.02},
        {"test": "3 · Phase at 50 Hz", "expected": 9.3,
         "actual": half_phase, "unit": "°", "tolerance": 0.2},
    ]
    for check in checks:
        check["passed"] = (abs(check["actual"] - check["expected"])
                           <= check["tolerance"])
    return json.dumps(checks, allow_nan=False)


def prediction_json(before_omega, after_omega, tau, guess):
    """Evaluate a saved prediction after the user increases frequency."""
    require_positive(before_omega=before_omega,
                     after_omega=after_omega, tau=tau)
    if after_omega <= before_omega:
        raise ValueError("Increase angular frequency before checking.")
    if guess not in ("increases", "decreases", "same"):
        raise ValueError("Choose a prediction first.")
    before_ratio = amplitude_ratio(before_omega, tau)
    after_ratio = amplitude_ratio(after_omega, tau)
    actual = ("decreases" if after_ratio < before_ratio else
              "increases" if after_ratio > before_ratio else "same")
    return json.dumps({
        "before_ratio": before_ratio,
        "after_ratio": after_ratio,
        "actual": actual,
        "correct": guess == actual,
    }, allow_nan=False)
