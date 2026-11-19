"""Homework 2 P2: first-order plant, PID feedback and a first-order sensor.

The numerical solution uses our own RK4 loop, not a library ODE solver.
All states start at zero. The setpoint is constant after its step at t=0.
D acts on the measured output, so the initial setpoint step has no D kick.
As in P1, the command is bounded and conditional integration prevents windup.
The deterministic sensor model gives its derivative directly; unlike P1's
finite-difference implementation, this experiment adds no derivative filter.
The command uses model units, not a measured motor's PWM calibration.
"""
import json
import math

DEFAULTS = {"K": 1.0, "tau": 1.0, "kp": 2.0, "ki": 4.0,
            "kd": 0.0, "sensor_tau": 0.05, "setpoint": 1.0, "duration": 30.0,
            "u_min": -100.0, "u_max": 100.0}


def settings(values):
    p = dict(DEFAULTS)
    p.update(values)
    for key in DEFAULTS:
        p[key] = float(p[key])
        if not math.isfinite(p[key]):
            raise ValueError(key + " must be a finite number.")
    if not 0.2 <= p["K"] <= 3 or not 0.2 <= p["tau"] <= 5:
        raise ValueError("Plant K must be 0.2–3 and plant tau must be 0.2–5 s.")
    if not 0 <= p["kp"] <= 12 or not 0 <= p["ki"] <= 12 or not 0 <= p["kd"] <= 0.5:
        raise ValueError("Use Kp and Ki from 0–12, and Kd from 0–0.5.")
    ts = p["sensor_tau"]
    if ts != 0 and not 0.02 <= ts <= 4:
        raise ValueError("Sensor tau_s must be 0 (ideal), or 0.02–4 s.")
    if not -2 <= p["setpoint"] <= 2 or not 5 <= p["duration"] <= 40:
        raise ValueError("Setpoint must be −2 to 2; duration must be 5–40 s.")
    if not -100 <= p["u_min"] <= 0 <= p["u_max"] <= 100 or p["u_min"] >= p["u_max"]:
        raise ValueError("Control limits must include zero: −100 ≤ minimum ≤ 0 ≤ maximum ≤ 100, with minimum < maximum.")
    return p


def signals(state, p):
    """Return the measured output, control command and state derivatives."""
    y, measured, integral = state
    K, tau = p["K"], p["tau"]
    kp, ki, kd, ts = p["kp"], p["ki"], p["kd"], p["sensor_tau"]
    if ts > 0:
        # Sensor: tau_s * d(measured)/dt + measured = true output.
        measured_rate = (y - measured) / ts
        error = p["setpoint"] - measured
        raw_control = kp * error + ki * integral - kd * measured_rate
    else:
        measured = y
        error = p["setpoint"] - y
        # With ideal measurement, substitute dy/dt=(K*u-y)/tau into D.
        raw_control = (kp * error + ki * integral + kd * y / tau) / (1 + K * kd / tau)
    control = max(p["u_min"], min(p["u_max"], raw_control))
    output_rate = (K * control - y) / tau
    if ts == 0:
        measured_rate = output_rate
    # Freeze the integral only if its next change would push further into a limit.
    pushing_high = raw_control > p["u_max"] and error > 0
    pushing_low = raw_control < p["u_min"] and error < 0
    integral_rate = 0.0 if ki > 0 and (pushing_high or pushing_low) else error
    return measured, control, [output_rate, measured_rate, integral_rate], raw_control != control


def rk4_step(state, h, p):
    """Four slopes, then their weighted average. Student-readable RK4."""
    k1 = signals(state, p)[2]
    midpoint1 = [x + h * slope / 2 for x, slope in zip(state, k1)]
    k2 = signals(midpoint1, p)[2]
    midpoint2 = [x + h * slope / 2 for x, slope in zip(state, k2)]
    k3 = signals(midpoint2, p)[2]
    endpoint = [x + h * slope for x, slope in zip(state, k3)]
    k4 = signals(endpoint, p)[2]
    return [x + h * (a + 2*b + 2*c + d) / 6
            for x, a, b, c, d in zip(state, k1, k2, k3, k4)]


def integrate(p, step_scale=1.0):
    """Choose a conservative internal step and keep at most ~1600 plot samples.

    The RK4 step is a simulation setting, not the digital PID sample time Ts.
    Faster sensor/plant modes need smaller steps; a cap bounds browser work.
    """
    h = min(0.01, p["tau"] / (10 * (1 + p["K"] * p["kp"])))
    if p["sensor_tau"] > 0:
        fast_time = p["tau"] * p["sensor_tau"] / (
            p["tau"] + p["sensor_tau"] + p["K"] * p["kd"])
        h = min(h, fast_time / 5)
    h *= step_scale
    count = math.ceil(p["duration"] / h)
    if count > 180000:
        raise ValueError("These settings need too many RK4 steps. Reduce duration or D, or increase tau_s.")
    h = p["duration"] / count
    stride = max(1, math.ceil(count / 1600))
    data = {"time": [], "true": [], "measured": [], "control": []}
    state = [0.0, 0.0, 0.0]
    stopped = False
    peak_ratio = 0.0
    saturation_count = 0
    for i in range(count + 1):
        measured, control, _, saturated = signals(state, p)
        saturation_count += int(saturated)
        if p["setpoint"] != 0:
            peak_ratio = max(peak_ratio, state[0] / p["setpoint"])
        if i % stride == 0 or i == count:
            data["time"].append(i * h)
            data["true"].append(state[0])
            data["measured"].append(measured)
            data["control"].append(control)
        if i == count:
            break
        candidate = rk4_step(state, h, p)
        if not all(math.isfinite(x) and abs(x) <= 1e6 for x in candidate):
            stopped = True
            if data["time"][-1] != i * h:
                data["time"].append(i * h)
                data["true"].append(state[0])
                data["measured"].append(measured)
                data["control"].append(control)
            break
        state = candidate
    data.update({"step": h, "steps": i, "stopped": stopped,
                 "peak_ratio": peak_ratio, "saturated": saturation_count > 0})
    return data


def metrics(data, p):
    y, measured, times = data["true"], data["measured"], data["time"]
    target = p["setpoint"]
    scale = max(abs(target), 1e-9)
    overshoot = None if target == 0 else max(0.0, data["peak_ratio"]-1) * 100
    tail = [v for t, v in zip(times, y) if t >= times[-1] - 6]
    previous = [v for t, v in zip(times, y) if times[-1]-12 <= t < times[-1]-6]
    amplitude = max(tail) - min(tail)
    previous_amplitude = max(previous)-min(previous) if previous else amplitude
    recent = [v for t, v in zip(times, y) if t >= times[-1]-12]
    crossings = sum((a-target)*(b-target) < 0 for a, b in zip(recent, recent[1:]))
    if data["stopped"]:
        motion = "Large response — simulation stopped"
    elif target == 0 or amplitude < 0.005*scale:
        motion = "Steady response"
    elif crossings >= 2 and amplitude > 0.03*scale:
        ratio = amplitude / max(previous_amplitude, 1e-12)
        motion = "Growing oscillation" if ratio > 1.15 else (
            "Ongoing oscillation" if ratio >= 0.85 else "Decaying oscillation")
    else:
        motion = "Response still changing"
    return {"overshoot": overshoot, "sensor_gap": max(abs(a-b) for a,b in zip(y,measured)),
            "last_error": target-y[-1], "motion": motion,
            "end_time": times[-1], "last_true": y[-1], "last_measured": measured[-1]}


def simulate(values, include_reference=True):
    p = settings(values)
    response = integrate(p)
    result = {"settings": p, "response": response, "metrics": metrics(response, p)}
    if include_reference:
        ideal = dict(p, sensor_tau=0.0)
        result["ideal"] = integrate(ideal)
    return result


def simulate_json(values_json):
    return json.dumps(simulate(json.loads(values_json)), allow_nan=False)


def crossing_time(times, values, level):
    for i in range(1, len(times)):
        if values[i-1] <= level <= values[i]:
            fraction = (level-values[i-1]) / (values[i]-values[i-1])
            return times[i-1] + fraction*(times[i]-times[i-1])
    return None


def validation_json():
    """Homework baselines use ideal feedback; P2 adds lag separately."""
    p = settings({"kp": 9, "ki": 0, "sensor_tau": 0, "duration": 5})
    response = integrate(p)
    tau_numeric = crossing_time(response["time"], response["true"], 0.9*(1-math.exp(-1)))
    pi = simulate({"kp": 1, "ki": 1, "sensor_tau": 0, "duration": 20}, False)
    # Ideal-feedback PI denominator: tau*s^2 + (1+K*kp)*s + K*ki.
    base = pi["settings"]
    a2 = base["tau"]
    a1 = 1 + base["K"] * base["kp"]
    a0 = base["K"] * base["ki"]
    wn = math.sqrt(a0 / a2)
    zeta = a1 / (2 * math.sqrt(a2 * a0))
    rows = [
        {"name": "P only: time constant", "expected": 0.1, "computed": tau_numeric, "tolerance": 0.0002, "unit": "s"},
        {"name": "P only: final step error", "expected": 10, "computed": 100*(1-response["true"][-1]), "tolerance": 0.01, "unit": "%"},
        {"name": "PI baseline: natural frequency", "expected": 1, "computed": wn, "tolerance": 1e-9, "unit": "rad/s"},
        {"name": "PI baseline: damping ratio", "expected": 1, "computed": zeta, "tolerance": 1e-9, "unit": ""},
        {"name": "Stable PI: step error at 20 s", "expected": 0, "computed": abs(pi["metrics"]["last_error"])*100, "tolerance": 0.01, "unit": "%"},
    ]
    for row in rows:
        row["passed"] = row["computed"] is not None and abs(row["computed"]-row["expected"]) <= row["tolerance"]
    return json.dumps(rows, allow_nan=False)
