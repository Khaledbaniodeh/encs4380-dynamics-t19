"""Ziegler–Nichols BONUS — independent from P4 scoring.

Student-readable numerical model: three first-order lags in series.

    Plant G(s) = 1 / (s + 1)^3
    State 1 -> State 2 -> Output

This plant has enough phase lag that increasing proportional gain can
produce sustained oscillations. A simple first-order plant cannot do that.

The functions below use ordinary Python only (no NumPy, no SciPy).
"""

# Ku = ultimate gain; Pu = period of sustained oscillation.
# Kp, Ki, Kd = controller gains calculated from Ku and Pu.

import json
import math

# These are physical time units, not P3's adjustable sampling period.
TIME_STEP = 0.025                  # 25 milliseconds for numerical RK4
DEMO_DURATION = 28.0              # enough to observe several oscillation cycles
SETPOINT = 1.0
MAX_ABSOLUTE_OUTPUT = 50000.0     # stop runaway plots instead of crashing


# 1. Third-order teaching plant and RK4 solver

def plant_derivatives(plant_state, control_input):
    """Rates of three unit-time-constant lags in a row.

    plant_state = (lag_one, lag_two, output).
    """
    lag_one, lag_two, output = plant_state
    return (control_input - lag_one,
            lag_one - lag_two,
            lag_two - output)


def rk4_step(state, derivative_function, step_size):
    """One explicit 4th-order Runge–Kutta update; no hidden library solver."""
    first = derivative_function(state)
    next_state = tuple(x + step_size * rate / 2 for x, rate in zip(state, first))
    second = derivative_function(next_state)
    next_state = tuple(x + step_size * rate / 2 for x, rate in zip(state, second))
    third = derivative_function(next_state)
    next_state = tuple(x + step_size * rate for x, rate in zip(state, third))
    fourth = derivative_function(next_state)
    return tuple(x + step_size * (a + 2*b + 2*c + d) / 6
                 for x, a, b, c, d in zip(state, first, second, third, fourth))


def validate_gain(value, label="P gain"):
    """Reject invalid user input clearly."""
    try:
        gain = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a number.") from error
    if not math.isfinite(gain) or not 0 < gain <= 14:
        raise ValueError(f"{label} must be greater than 0 and at most 14.")
    return gain


def find_peak_positions(values):
    """Indexes where output changes from rising to falling."""
    return [i for i in range(1, len(values)-1)
            if values[i-1] < values[i] and values[i] >= values[i+1]]


# 2. P-only experiment: observe growing or fading oscillations

def simulate_p_only(proportional_gain, duration=DEMO_DURATION, dt=TIME_STEP):
    """Closed-loop P-only response: u = Kp * (1 - y).

    Collect the *full* time series for peak detection. Return decimated
    samples for charting, so mobile phones do not get giant chart data.
    """
    gain = validate_gain(proportional_gain)
    number_of_steps = round(duration / dt)
    if number_of_steps <= 10:
        raise ValueError("Duration too short for a response plot.")
    actual_step = duration / number_of_steps
    plant_state = (0.0, 0.0, 0.0)
    times, outputs = [], []
    for step_index in range(number_of_steps + 1):
        time = step_index * actual_step
        output = plant_state[2]
        if not math.isfinite(output) or abs(output) > MAX_ABSOLUTE_OUTPUT:
            raise ValueError("Response grew too large. Reduce the proportional gain.")
        times.append(time)
        outputs.append(output)
        if step_index < number_of_steps:
            def rates(state):
                current_output = state[2]
                control = gain * (SETPOINT - current_output)
                return plant_derivatives(state, control)
            plant_state = rk4_step(plant_state, rates, actual_step)

    steady_level = gain / (1.0 + gain)  # equilibrium for P-only unity feedback
    peaks = find_peak_positions(outputs)
    peak_times = [times[index] for index in peaks]
    peak_amplitudes = [abs(outputs[index] - steady_level) for index in peaks]
    if len(peaks) >= 2 and peak_amplitudes[-2] > 1e-9 and peak_amplitudes[-1] > 1e-9:
        period = peak_times[-1] - peak_times[-2]
        growth_rate = math.log(peak_amplitudes[-1] / peak_amplitudes[-2]) / period
        # Growth near 0 means successive peaks keep the same height.
        if growth_rate > 0.005:
            behavior = "growing"
        elif growth_rate < -0.005:
            behavior = "decaying"
        else:
            behavior = "sustained"
    else:
        growth_rate = None
        period = None
        behavior = "no_clear_peaks"

    chart_stride = max(1, math.ceil(len(times) / 480))
    chart_indexes = list(range(0, len(times), chart_stride))
    if chart_indexes[-1] != len(times)-1:
        chart_indexes.append(len(times)-1)
    return {
        "gain": gain, "steady_level": round(steady_level, 5),
        "behavior": behavior, "growth_rate": growth_rate,
        "period_seconds": period,
        "peak_times": peak_times,
        "time": [round(times[index], 4) for index in chart_indexes],
        "output": [round(outputs[index], 6) for index in chart_indexes],
    }


# 3. Search for Ku and measure Pu using peak detection

def find_ultimate_gain():
    """Numerically find where successive peak amplitudes stop shrinking.

    We know a search bracket for this *teaching plant*: a P-only gain of 6
    damps the oscillations, while 10 causes growth. Bisection repeatedly
    simulates the loop and looks at peak-amplitude growth — not a hardcoded Ku.
    """
    low_gain, high_gain = 6.0, 10.0
    for _ in range(15):
        middle_gain = (low_gain + high_gain) / 2
        trial = simulate_p_only(middle_gain)
        growth = trial["growth_rate"]
        if growth is None:
            raise RuntimeError("Could not measure peaks during the gain search.")
        if growth > 0:
            high_gain = middle_gain
        else:
            low_gain = middle_gain

    ultimate_gain = (low_gain + high_gain) / 2
    critical_trial = simulate_p_only(ultimate_gain)
    if critical_trial["period_seconds"] is None:
        raise RuntimeError("The oscillation period could not be measured.")
    return {
        "ultimate_gain": ultimate_gain,
        "ultimate_period": critical_trial["period_seconds"],
        "response": critical_trial,
        "search_iterations": 15,
        "method": "RK4 + peak detection + bisection",
    }


# 4. Ziegler–Nichols rules for Kp, Ki and Kd

def ziegler_nichols_pid_gains(ultimate_gain, ultimate_period):
    """Classic ZN closed-loop/ultimate-gain rule, in *parallel* PID form.

    Kp = 0.6 Ku
    Ki = Kp/Ti, with Ti = Pu/2  ->  Ki = 1.2 Ku/Pu
    Kd = Kp*Td, with Td = Pu/8 ->  Kd = 0.075 Ku*Pu
    """
    ku = float(ultimate_gain)
    pu = float(ultimate_period)
    if not math.isfinite(ku) or not math.isfinite(pu) or ku <= 0 or pu <= 0:
        raise ValueError("Ultimate gain and period must be positive and finite.")
    return {"kp": 0.6 * ku, "ki": 1.2 * ku / pu, "kd": 0.075 * ku * pu,
            "integral_time": pu / 2, "derivative_time": pu / 8}


# 5. Compare Ziegler–Nichols PID against the P-only experiment

def simulate_pid(pid_gains, duration=DEMO_DURATION, dt=TIME_STEP):
    """Simulate the same three-lag plant with continuous-time PID action.

    We differentiate the *output*, which prevents a derivative kick when
    the step setpoint is applied. There is no actuator saturation in this
    bonus demonstration; this is separate from P4's ±10-limited challenge.
    """
    kp, ki, kd = (float(pid_gains[name]) for name in ("kp", "ki", "kd"))
    if not all(math.isfinite(x) and x >= 0 for x in (kp, ki, kd)):
        raise ValueError("All PID gains must be finite and nonnegative.")
    number_of_steps = round(duration / dt)
    actual_step = duration / number_of_steps
    # state = lag1, lag2, output, integrated_error
    state = (0.0, 0.0, 0.0, 0.0)
    times, outputs = [], []
    for step_index in range(number_of_steps+1):
        time = step_index * actual_step
        output = state[2]
        if not math.isfinite(output) or abs(output) > MAX_ABSOLUTE_OUTPUT:
            raise ValueError("PID response diverged; tuning is unstable.")
        times.append(time)
        outputs.append(output)
        if step_index < number_of_steps:
            def rates(current_state):
                lag1, lag2, measured_output, integrated_error = current_state
                tracking_error = SETPOINT - measured_output
                measured_output_rate = lag2 - measured_output
                command = kp * tracking_error + ki * integrated_error - kd * measured_output_rate
                return (*plant_derivatives((lag1, lag2, measured_output), command),
                        tracking_error)
            state = rk4_step(state, rates, actual_step)

    highest_output = max(outputs)
    overshoot = max(0.0, highest_output - SETPOINT) * 100
    final_error = abs(SETPOINT - outputs[-1]) * 100
    band = 0.02
    last_outside = max((i for i, output in enumerate(outputs) if abs(output-SETPOINT) > band), default=-1)
    settling_time = None
    if last_outside < len(outputs)-1 and (duration - (last_outside+1)*actual_step) >= 0.5:
        settling_time = (last_outside+1)*actual_step
    chart_stride = max(1, math.ceil(len(times) / 480))
    chart_indexes = list(range(0, len(times), chart_stride))
    if chart_indexes[-1] != len(times)-1:
        chart_indexes.append(len(times)-1)
    return {"time": [round(times[i], 4) for i in chart_indexes],
            "output": [round(outputs[i], 6) for i in chart_indexes],
            "overshoot_percent": round(overshoot, 2),
            "settling_time": round(settling_time, 2) if settling_time is not None else None,
            "final_error_percent": round(final_error, 3)}


# 6. Functions used by the JavaScript page (Pyodide)

def test_gain_json(gain_json):
    """Browser bridge: inspect one user-selected P-only gain."""
    return json.dumps(simulate_p_only(float(gain_json)), allow_nan=False)


def calculate_bonus_json():
    """Browser bridge: determine Ku/Pu, compute gains, and compare curves."""
    discovery = find_ultimate_gain()
    gains = ziegler_nichols_pid_gains(discovery["ultimate_gain"], discovery["ultimate_period"])
    tuned_response = simulate_pid(gains)
    return json.dumps({"discovery": discovery, "gains": gains,
                       "tuned_response": tuned_response}, allow_nan=False)