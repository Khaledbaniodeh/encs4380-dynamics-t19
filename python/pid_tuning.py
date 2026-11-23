"""P4 — PID Tuning Challenge (ENCS4380 HW2).

No external Python packages. The solver advances a real closed-loop model in time,
using a hand-written RK4 plant step (not a closed-form step response).
The random plant is kept behind the challenge interface until explicitly revealed.
"""

# Names used in the formulas: y = plant output, u = control input.
# K = plant gain, tau = time constant, zeta = damping ratio, omega_n = natural frequency.
# Kp, Ki, Kd = proportional, integral and derivative PID gains.

from __future__ import annotations

import json
import math
import random

DT = 0.008
DURATION = 16.0
CONTROL_LIMIT = 10.0
MAX_OUTPUT = 1e5


# 1. Validate the user inputs

def _finite(value: object, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number.") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite.")
    return number


def validate_gains(gains: dict) -> dict:
    ranges = {"kp": (0.0, 12.0), "ki": (0.0, 12.0), "kd": (0.0, 3.0)}
    clean = {}
    for name, (minimum, maximum) in ranges.items():
        value = _finite(gains.get(name), name.upper())
        if value < minimum or value > maximum:
            raise ValueError(f"{name.upper()} must be between {minimum:g} and {maximum:g}.")
        clean[name] = value
    return clean


# 2. Plant equations and RK4 numerical solver

def _plant_derivatives(state: tuple[float, float], control: float, plant: dict) -> tuple[float, float]:
    y, velocity = state
    if plant["type"] == "first_order":
        return (plant["K"] * control - y) / plant["tau"], 0.0
    wn = plant["omega_n"]
    return velocity, plant["K"] * wn * wn * control - 2 * plant["zeta"] * wn * velocity - wn * wn * y


def _rk4_plant_step(state: tuple[float, float], control: float, plant: dict, dt: float) -> tuple[float, float]:
    # Zero-order-hold control during this small step; RK4 for plant dynamics.
    k1 = _plant_derivatives(state, control, plant)
    s2 = tuple(s + 0.5 * dt * k for s, k in zip(state, k1))
    k2 = _plant_derivatives(s2, control, plant)
    s3 = tuple(s + 0.5 * dt * k for s, k in zip(state, k2))
    k3 = _plant_derivatives(s3, control, plant)
    s4 = tuple(s + dt * k for s, k in zip(state, k3))
    k4 = _plant_derivatives(s4, control, plant)
    return tuple(s + dt * (a + 2*b + 2*c + d) / 6 for s, a, b, c, d in zip(state, k1, k2, k3, k4))



# 3. Gray reference curve: plant without PID

def simulate_open_loop(plant: dict, duration: float = DURATION, dt: float = DT) -> dict:
    """Visible initial plant response to a **unit actuator step** u(t)=1.

    This is not the closed-loop response for any PID gains. It is a preview of
    the unknown plant's dynamics before the player chooses a controller. The
    plant parameters and the hidden reference PID are never returned here.
    It uses the same handwritten RK4 integrator and time samples as simulate().
    """
    duration = _finite(duration, "Duration")
    dt = _finite(dt, "Integration step")
    if not (2 <= duration <= 40 and 0 < dt <= .025):
        raise ValueError("Duration must be 2–40 s and integration step <= 0.025 s.")
    if plant["type"] not in ("first_order", "second_order"):
        raise ValueError("Unknown plant type.")
    count = math.ceil(duration / dt)
    step = duration / count
    stride = max(1, math.ceil(count / 700))
    state = (0.0, 0.0)
    times, output = [], []
    for i in range(count + 1):
        y = state[0]
        if not math.isfinite(y) or abs(y) > MAX_OUTPUT:
            raise ValueError("Open-loop plant response is not finite.")
        if i % stride == 0 or i == count:
            times.append(round(i*step, 5))
            output.append(y)
        if i != count:
            state = _rk4_plant_step(state, 1.0, plant, step)
    return {"time": times, "output": output}

# 4. Closed-loop PID response and performance metrics

def simulate(plant: dict, gains: dict, duration: float = DURATION, dt: float = DT) -> dict:
    """Closed-loop unity-feedback PID step response, with limits and anti-windup.

    D uses filtered *output* rate to avoid derivative kick at step onset.
    RK4 steps the plant with a held command; controller updates every dt.
    This dt is the numerical integration/controller-update step, NOT P3's
    user-controlled sampling-time experiment.
    """
    gains = validate_gains(gains)
    duration = _finite(duration, "Duration")
    dt = _finite(dt, "Integration step")
    if not (2 <= duration <= 40 and 0 < dt <= .025):
        raise ValueError("Duration must be 2–40 s and integration step <= 0.025 s.")
    if plant["type"] == "first_order":
        if not (plant["K"] > 0 and plant["tau"] > 0):
            raise ValueError("Invalid first-order plant.")
    elif plant["type"] == "second_order":
        if not (plant["K"] > 0 and plant["omega_n"] > 0 and plant["zeta"] > 0):
            raise ValueError("Invalid second-order plant.")
    else:
        raise ValueError("Unknown plant type.")

    count = math.ceil(duration / dt)
    step = duration / count
    stride = max(1, math.ceil(count / 700))
    state = (0.0, 0.0)
    integral = 0.0
    filtered_rate = 0.0
    last_rate = 0.0
    rate_filter_tau = .045
    times, output, control = [], [], []
    history = []
    peak = 0.0
    saturation_count = 0
    stopped = False

    for i in range(count + 1):
        t = i * step
        y = state[0]
        if not math.isfinite(y) or abs(y) > MAX_OUTPUT:
            stopped = True
            break
        error = 1.0 - y  # Setpoint is a unit step in P4.
        if i:
            filt_alpha = step / (rate_filter_tau + step)
            filtered_rate += filt_alpha * (last_rate - filtered_rate)
        raw_u = gains["kp"] * error + gains["ki"] * integral - gains["kd"] * filtered_rate
        u = min(CONTROL_LIMIT, max(-CONTROL_LIMIT, raw_u))
        saturated = abs(raw_u - u) > 1e-10
        saturation_count += int(saturated)
        peak = max(peak, y)
        history.append((t, y))
        if i % stride == 0 or i == count:
            times.append(round(t, 5))
            output.append(y)
            control.append(u)
        if i == count:
            break
        # Conditional integration: prevent worsening saturation (anti-windup).
        pushing_into_limit = (raw_u > CONTROL_LIMIT and error > 0) or (raw_u < -CONTROL_LIMIT and error < 0)
        if not pushing_into_limit:
            integral = min(100.0, max(-100.0, integral + step * error))
        prior_y = y
        state = _rk4_plant_step(state, u, plant, step)
        last_rate = (state[0] - prior_y) / step

    if stopped:
        # Explicit failure metrics: do not pass an unstable or divergent trajectory.
        metrics = {"overshoot_percent": None, "settling_time": None, "steady_error_percent": None,
                   "final_output": None, "saturated_percent": round(100*saturation_count/max(1,len(history)), 2),
                   "diverged": True}
    else:
        final_y = history[-1][1]
        # Last exit from the ±2% band determines the settling time.
        last_outside = -1
        for j, (_, value) in enumerate(history):
            if abs(value - 1.0) > .02:
                last_outside = j
        settle = None
        if last_outside < len(history) - 1:
            candidate = history[last_outside + 1][0]
            if duration - candidate >= .5:  # do not mistake one endpoint for settling
                settle = candidate
        # A final near-zero error does not imply steady output if oscillating.
        tail = [v for t, v in history if t >= duration - 1.0]
        tail_span = max(tail) - min(tail) if tail else 0.0
        metrics = {"overshoot_percent": round(max(0, peak - 1.0) * 100, 3),
                   "settling_time": round(settle, 4) if settle is not None else None,
                   "steady_error_percent": round(abs(1-final_y) * 100, 3),
                   "final_output": round(final_y, 6),
                   "saturated_percent": round(100*saturation_count/len(history), 2),
                   "tail_span_percent": round(tail_span * 100, 3),
                   "diverged": False}
    return {"time": times, "output": output, "control": control, "metrics": metrics}


# 5. Pass/Fail scoring

def evaluate(metrics: dict, specs: dict) -> dict:
    if metrics["diverged"]:
        passes = {"overshoot": False, "settling": False, "steady_error": False}
    else:
        passes = {
            "overshoot": metrics["overshoot_percent"] <= specs["overshoot_max_percent"] + 1e-8,
            "settling": (metrics["settling_time"] is not None and
                         metrics["settling_time"] <= specs["settling_max_seconds"] + 1e-8),
            "steady_error": (metrics["steady_error_percent"] <= specs["steady_error_max_percent"] + 1e-8
                             and metrics["tail_span_percent"] <= 1.0),
        }
    score = round(100 * sum(passes.values()) / 3, 2)
    return {"passes": passes, "score": score, "all_pass": all(passes.values())}


# 6. Generate random but solvable challenges

def _reference_choices(plant: dict) -> list[dict]:
    if plant["type"] == "first_order":
        out = []
        for wn in [1.7, 2.1, 2.5, 2.9]:
            for zeta in [0.9, 1.0]:
                kp = (2 * zeta * wn * plant["tau"] - 1) / plant["K"]
                ki = plant["tau"] * wn*wn / plant["K"]
                if 0 <= kp <= 12 and 0 <= ki <= 12:
                    out.append({"kp": kp, "ki": ki, "kd": 0})
        return out
    return [{"kp": kp, "ki": ki, "kd": kd} for kp, ki, kd in [
        (1.0, .9, 1.0), (1.5, 1.1, 1.0), (2, 1.5, 1.2),
        (2.5, 1.6, 1.4), (3.0, 2.0, 1.5), (4, 2.0, 1.8),
        (3, 1.2, 1.0), (4, 1.5, 2.0), (2, .8, 1.5),
        (3.5, 1.8, 2.4), (5, 2.5, 2.0), (5, 1.5, 2.5)
    ]]


# Four intentionally different response families. The values within each family
# remain random and hidden, but the challenge generator avoids serving several
# look-alike baseline curves in a row. Unlike hardcoded demonstration traces,
# each curve comes from the real RK4 integration of the sampled plant.
PLANT_FAMILIES = ("first_fast", "first_slow", "second_oscillatory", "second_damped")
FAMILY_TYPES = {
    "first_fast": "first_order", "first_slow": "first_order",
    "second_oscillatory": "second_order", "second_damped": "second_order",
}


def _sample_plant(rng: random.Random, family: str) -> dict:
    kind = FAMILY_TYPES[family]
    if kind == "first_order":
        # Visible change in rise speed and steady-state gain on an 8 s plot.
        tau_range = (.3, .72) if family == "first_fast" else (1.45, 2.55)
        return {"type": kind, "K": round(rng.uniform(.65, 1.6), 3),
                "tau": round(rng.uniform(*tau_range), 3)}
    # An oscillatory case has clearly visible peaks; a heavily damped case
    # has none or very little. Both are valid second-order physical models.
    damping_range = (.18, .38) if family == "second_oscillatory" else (.8, 1.2)
    return {"type": kind, "K": round(rng.uniform(.65, 1.55), 3),
            "zeta": round(rng.uniform(*damping_range), 3),
            "omega_n": round(rng.uniform(1.25, 3.25), 3)}


def generate_challenge(rng: random.Random | None = None, forced_type: str | None = None,
                       forced_family: str | None = None) -> dict:
    """Generate a hidden random plant with genuinely varied, feasible dynamics.

    First and second order both have fast/slow or oscillatory/damped examples.
    Each candidate must pass every specification under a hidden reference PID.
    No reference gain or plant parameter is sent with the public challenge.
    """
    rng = rng or random.Random()
    if forced_type not in (None, "first_order", "second_order"):
        raise ValueError("Invalid plant type.")
    if forced_family is not None and forced_family not in PLANT_FAMILIES:
        raise ValueError("Invalid response family.")
    if forced_family is not None and forced_type is not None and FAMILY_TYPES[forced_family] != forced_type:
        raise ValueError("Response family does not match plant type.")
    families = [f for f in PLANT_FAMILIES if forced_type is None or FAMILY_TYPES[f] == forced_type]
    if forced_family is not None:
        families = [forced_family]
    # After a failed candidate, keep the same family: don't silently reject
    # the visually different cases in favour of familiar gentle curves.
    family = rng.choice(families)
    for attempt in range(35):
        plant = _sample_plant(rng, family)
        viable = []
        for gains in _reference_choices(plant):
            m = simulate(plant, gains)["metrics"]
            if (not m["diverged"] and m["settling_time"] is not None
                    and m["overshoot_percent"] <= 9.0
                    and m["steady_error_percent"] <= .5
                    and m["tail_span_percent"] <= .5
                    and m["settling_time"] <= 8.0):
                viable.append((m["settling_time"], gains))
        if viable:
            best_settle, reference_gains = min(viable, key=lambda pair: pair[0])
            limit = max(2.0, min(9.0, math.ceil((best_settle*1.25 + .45)*2)/2))
            specs = {"overshoot_max_percent": 10.0,
                     "settling_max_seconds": limit,
                     "steady_error_max_percent": 1.0}
            return {"plant": plant, "specs": specs, "reference_gains": reference_gains,
                    "family": family}
    raise RuntimeError("Could not produce a feasible tuning challenge.")


_ACTIVE: dict | None = None
_CHALLENGE_INDEX = 0
_FAMILY_BAG: list[str] = []


# 7. Functions used by the JavaScript page (Pyodide)

def new_challenge_json() -> str:
    global _ACTIVE, _CHALLENGE_INDEX, _FAMILY_BAG
    # Each group of four challenges visits all four response families in a
    # randomized order. This is a variety constraint, not a fixed plant:
    # parameters are newly random every time.
    if not _FAMILY_BAG:
        _FAMILY_BAG = list(PLANT_FAMILIES)
        random.shuffle(_FAMILY_BAG)
    family = _FAMILY_BAG.pop()
    _ACTIVE = generate_challenge(forced_family=family)
    _CHALLENGE_INDEX += 1
    # Expose only a plotted open-loop *output*, not the plant parameters or
    # the private reference gains. This is safe for a teaching challenge.
    baseline = simulate_open_loop(_ACTIVE["plant"])
    return json.dumps({"challenge_number": _CHALLENGE_INDEX,
                       "plant_type": _ACTIVE["plant"]["type"],
                       "specs": _ACTIVE["specs"],
                       "setpoint": 1.0, "control_limit": CONTROL_LIMIT,
                       "baseline": baseline}, allow_nan=False)


def check_tuning_json(gains_json: str) -> str:
    if _ACTIVE is None:
        raise ValueError("Start a challenge first.")
    gains = validate_gains(json.loads(gains_json))
    result = simulate(_ACTIVE["plant"], gains)
    report = evaluate(result["metrics"], _ACTIVE["specs"])
    return json.dumps({"time": result["time"], "output": result["output"],
                       "control": result["control"], "metrics": result["metrics"],
                       "passes": report["passes"], "score": report["score"],
                       "all_pass": report["all_pass"]}, allow_nan=False)


def reveal_plant_json() -> str:
    if _ACTIVE is None:
        raise ValueError("Start a challenge first.")
    return json.dumps(_ACTIVE["plant"])