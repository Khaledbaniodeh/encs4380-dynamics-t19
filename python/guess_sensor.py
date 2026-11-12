"""Module 4: Guess the Sensor — mathematical model and scoring.

This module runs in the browser through Pyodide; no server-side Python is used.
All challenges use a UNIT input amplitude (A=1).

First order:       G(s) = K/(tau*s+1)
Second order:      G(s) = omega_n**2 / (s**2+2*zeta*omega_n*s+omega_n**2)

Only positive parameters are generated. The second-order challenges are
underdamped (0<zeta<1) so the peak-time/overshoot estimation method applies.
"""

import math
import random


def first_order_step(t, gain, tau):
    """Zero-initial-output response to a unit step."""
    if not all(math.isfinite(v) for v in (t, gain, tau)) or t < 0 or gain <= 0 or tau <= 0:
        raise ValueError("Require finite t>=0, K>0 and tau>0.")
    return gain * (-math.expm1(-t / tau))


def first_order_sine(t, gain, tau, omega):
    """Steady-state sinusoidal output for unit input sin(omega*t).

    Input:  x(t) = sin(omega*t)
    Output: y(t) = K*M*sin(omega*t + phi),
    M = 1/sqrt(1+(omega*tau)^2), phi = -atan(omega*tau).

    Note this is a STEADY-STATE sine (initial transient already decayed).
    """
    if (not all(math.isfinite(v) for v in (t, gain, tau, omega)) or
            t < 0 or gain <= 0 or tau <= 0 or omega <= 0):
        raise ValueError("Require finite t>=0, K>0, tau>0 and omega>0.")
    magnitude_ratio = 1.0 / math.sqrt(1.0 + (omega * tau) ** 2)
    phase_lag = -math.atan(omega * tau)
    return gain * magnitude_ratio * math.sin(omega * t + phase_lag)


def second_order_step(t, zeta, omega_n):
    """Underdamped second-order response to a unit step (unit DC gain)."""
    if (not all(math.isfinite(v) for v in (t, zeta, omega_n)) or
            t < 0 or not 0 < zeta < 1 or omega_n <= 0):
        raise ValueError("Require finite t>=0, 0<zeta<1 and omega_n>0.")
    root = math.sqrt(1.0 - zeta * zeta)
    omega_d = omega_n * root
    return 1.0 - math.exp(-zeta * omega_n * t) * (
        math.cos(omega_d * t) + (zeta / root) * math.sin(omega_d * t)
    )


def new_sensor(rng=None, *, sensor_type=None, response_kind=None):
    """Build an estimable random challenge with noisy samples.

    sensor_type and response_kind are OPTIONAL test controls, not UI options.
    The browser uses new_sensor() without overrides and cannot choose values.
    Returns clean/noisy data plus true values, which the browser keeps hidden
    until the user submits a guess.
    """
    if rng is None:
        rng = random.Random()
    if sensor_type is None:
        sensor_type = rng.choice(("first_order", "second_order"))
    if sensor_type not in ("first_order", "second_order"):
        raise ValueError("Invalid sensor type.")

    if response_kind is None:
        # About 35% of FIRST-order challenges are sines, the rest are steps.
        response_kind = ("sine" if rng.random() < 0.35 else "step") if sensor_type == "first_order" else "step"
    if response_kind not in ("step", "sine") or (sensor_type == "second_order" and response_kind != "step"):
        raise ValueError("Only first-order sensors support sine challenges.")

    input_amplitude = 1.0
    frequency = None

    if sensor_type == "first_order":
        gain = round(rng.uniform(0.8, 3.0), 2)
        tau = round(rng.uniform(0.6, 4.0), 2)
        parameters = {"K": gain, "tau": tau}
        if response_kind == "sine":
            # Keep omega*tau informative, avoiding imperceptible phase/amplitude changes.
            frequency = round(rng.uniform(0.65, 1.8) / tau, 3)
            period = 2.0 * math.pi / frequency
            duration = 4.0 * period
            response = lambda t: first_order_sine(t, gain, tau, frequency)
            input_signal = lambda t: math.sin(frequency * t)
            sample_count = 321  # 80 samples per cycle.
            noise_std = 0.02 * gain / math.sqrt(1.0 + (frequency * tau) ** 2)
        else:
            duration = 5.0 * tau  # Includes the 63.2% point and approaches final gain.
            response = lambda t: first_order_step(t, gain, tau)
            input_signal = None
            sample_count = 241
            noise_std = 0.015 * gain
    else:
        zeta = round(rng.uniform(0.20, 0.65), 2)
        omega_n = round(rng.uniform(1.0, 5.0), 2)
        parameters = {"zeta": zeta, "omega_n": omega_n}
        duration = max(10.0 / omega_n, 7.0 / (zeta * omega_n))
        response = lambda t: second_order_step(t, zeta, omega_n)
        input_signal = None
        sample_count = 241
        noise_std = 0.015

    time = [duration * i / (sample_count - 1) for i in range(sample_count)]
    clean_response = [response(t) for t in time]
    noisy_response = [val + rng.gauss(0.0, noise_std) for val in clean_response]
    if response_kind == "step":
        noisy_response[0] = 0.0  # Known zero initial condition for step challenges.

    return {
        "type": sensor_type,
        "response_kind": response_kind,
        "frequency": frequency,            # Public challenge information.
        "input_amplitude": input_amplitude,
        "input_signal": [input_signal(t) for t in time] if input_signal else None,
        "parameters": parameters,           # HIDDEN until submit.
        "time": time,
        "clean_response": clean_response,  # HIDDEN until submit.
        "noisy_response": noisy_response,  # Visible during guessing.
    }


def reveal_guess(challenge, guess):
    """Return true values and the curve predicted by the submitted guess."""
    t_values = challenge["time"]
    if challenge["type"] == "first_order":
        gain = float(guess["K"])
        tau = float(guess["tau"])
        if not all(math.isfinite(v) for v in (gain, tau)) or gain <= 0 or tau <= 0:
            raise ValueError("Require positive finite K and tau.")
        if challenge["response_kind"] == "sine":
            omega = challenge["frequency"]
            predicted = [first_order_sine(t, gain, tau, omega) for t in t_values]
        else:
            predicted = [first_order_step(t, gain, tau) for t in t_values]
    elif challenge["type"] == "second_order":
        zeta = float(guess["zeta"])
        omega_n = float(guess["omega_n"])
        if not all(math.isfinite(v) for v in (zeta, omega_n)) or not 0 < zeta < 1 or omega_n <= 0:
            raise ValueError("Require finite 0<zeta<1 and omega_n>0.")
        predicted = [second_order_step(t, zeta, omega_n) for t in t_values]
    else:
        raise ValueError("Unknown sensor type.")
    return {
        "parameters": challenge["parameters"],
        "clean_response": challenge["clean_response"],
        "predicted_response": predicted,
    }


def parameter_score(guess, actual):
    """Fair score: 100 if error <=10%; linear to zero at 100% error.

    Relative error = |guess - actual| / actual * 100.
    All possible *true* generated parameters are >0 (no zero denominator).
    """
    if not all(math.isfinite(v) for v in (guess, actual)) or actual <= 0:
        raise ValueError("Require positive finite actual and finite guess.")
    error = abs(guess - actual) / actual * 100.0
    # Extremely large but finite inputs may overflow the ratio in floating point.
    # Keep the displayed error finite so JSON can always be parsed by JavaScript.
    if not math.isfinite(error):
        error = 1_000_000_000.0
    if error <= 10.0 + 1e-10:
        points = 100.0
    elif error >= 100.0:
        points = 0.0
    else:
        points = 100.0 * (100.0 - error) / 90.0
    return {"error_percent": round(error, 2), "score": round(points, 2)}


def score_guess(challenge, guess):
    """Two parameters, equal weight: 50% each, total 0..100."""
    names = ("K", "tau") if challenge["type"] == "first_order" else ("zeta", "omega_n")
    results = {
        name: parameter_score(float(guess[name]), challenge["parameters"][name])
        for name in names
    }
    score = round(sum(result["score"] for result in results.values()) / 2.0, 2)
    return {"parameters": results, "round_score": score}
