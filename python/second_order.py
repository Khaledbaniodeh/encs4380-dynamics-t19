
from math import sqrt, pi, exp, sin, cos
import json


def damping_type(zeta):
    if zeta < 1:
        return "Underdamped"
    if abs(zeta - 1) < 1e-9:
        return "Critically damped"
    return "Overdamped"


def poles(zeta, wn):
    real = -zeta * wn

    if zeta < 1:
        imag = wn * sqrt(1 - zeta ** 2)
        return [{"re": real, "im": imag}, {"re": real, "im": -imag}]

    if abs(zeta - 1) < 1e-9:
        return [{"re": -wn, "im": 0}, {"re": -wn, "im": 0}]

    root = wn * sqrt(zeta ** 2 - 1)
    return [{"re": real + root, "im": 0}, {"re": real - root, "im": 0}]


def physical_values(m, b, k):
    wn = sqrt(k / m)
    zeta = b / (2 * sqrt(k * m))
    A = [[0, 1], [-k / m, -b / m]]
    B = [0, 1 / m]

    return wn, zeta, A, B


def eigenvalues(A):
    trace = A[0][0] + A[1][1]
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    d = trace ** 2 / 4 - det

    if d >= 0:
        root = sqrt(d)
        return [{"re": trace / 2 + root, "im": 0}, {"re": trace / 2 - root, "im": 0}]

    imag = sqrt(-d)
    return [{"re": trace / 2, "im": imag}, {"re": trace / 2, "im": -imag}]


def simulation_settings(zeta, wn):
    if zeta > 1:
        root = sqrt(zeta ** 2 - 1)
        slow = wn / (zeta + root)
        fast = wn * (zeta + root)
        settling_estimate = 4 / slow

    elif zeta >= 1 - 1e-9:
        fast = wn
        settling_estimate = 5.83 / wn

    elif zeta > 0:
        fast = wn
        settling_estimate = 4 / (zeta * wn)

    else:
        dt = 1 / (40 * wn)
        end_time = 10 * pi / wn
        return dt, end_time

    dt = min(0.01, 1 / (40 * fast))
    end_time = max(10 / wn, 1.5 * settling_estimate)

    return dt, end_time


# Closed-form second-order step response
def closed_form_response(zeta, wn, gain, step, dt, end_time):
    final_value = gain * step
    steps = round(end_time / dt)
    max_steps = 2500

    if steps > max_steps:
        steps = max_steps
        dt = end_time / steps

    time = []
    position = []
    velocity = []

    for i in range(steps + 1):
        t = i * dt
        time.append(t)

        # Underdamped
        if zeta < 1 - 1e-9:
            root = sqrt(1 - zeta ** 2)
            wd = wn * root
            decay = exp(-zeta * wn * t)

            y = final_value * (1 - decay * (cos(wd * t) + (zeta / root) * sin(wd * t)))
            v = final_value * wn / root * decay * sin(wd * t)

        # Critically damped
        elif abs(zeta - 1) <= 1e-9:
            decay = exp(-wn * t)

            y = final_value * (1 - decay * (1 + wn * t))
            v = final_value * wn ** 2 * t * decay

        # Overdamped
        else:
            root = wn * sqrt(zeta ** 2 - 1)
            s1 = -zeta * wn + root
            s2 = -zeta * wn - root
            e1 = exp(s1 * t)
            e2 = exp(s2 * t)

            y = final_value * (1 + (s2 * e1 - s1 * e2) / (s1 - s2))
            v = final_value * s1 * s2 * (e1 - e2) / (s1 - s2)

        position.append(y)
        velocity.append(v)

    return time, position, velocity


# RK4 numerical solver kept for optional comparison / bonus work
def rk4(A, B, u, dt, end_time):
    x = [0.0, 0.0]

    time = [0.0]
    x1 = [0.0]
    x2 = [0.0]

    steps = round(end_time / dt)
    max_steps = 10000

    if steps > max_steps:
        steps = max_steps
        dt = end_time / steps

    def f(state):
        return [
            A[0][0] * state[0] + A[0][1] * state[1] + B[0] * u,
            A[1][0] * state[0] + A[1][1] * state[1] + B[1] * u
        ]

    for n in range(steps):
        k1 = f(x)
        k2 = f([x[0] + dt * k1[0] / 2, x[1] + dt * k1[1] / 2])
        k3 = f([x[0] + dt * k2[0] / 2, x[1] + dt * k2[1] / 2])
        k4 = f([x[0] + dt * k3[0], x[1] + dt * k3[1]])

        x[0] += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        x[1] += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])

        time.append((n + 1) * dt)
        x1.append(x[0])
        x2.append(x[1])

    return time, x1, x2


def crossing_time(t1, y1, t2, y2, target):
    if y2 == y1:
        return t2

    return t1 + (target - y1) * (t2 - t1) / (y2 - y1)


def metrics(time, y, final_value):
    if final_value == 0:
        return {
            "rise_time": None,
            "peak_time": None,
            "peak_value": None,
            "overshoot_percent": None,
            "settling_time": None
        }

    normalized = [value / final_value for value in y]

    t10 = None
    t90 = None

    for i in range(1, len(normalized)):
        y1 = normalized[i - 1]
        y2 = normalized[i]

        if t10 is None and y1 < 0.1 <= y2:
            t10 = crossing_time(time[i - 1], y1, time[i], y2, 0.1)

        if t90 is None and y1 < 0.9 <= y2:
            t90 = crossing_time(time[i - 1], y1, time[i], y2, 0.9)

    rise_time = None if t10 is None or t90 is None else t90 - t10

    peak_index = max(range(len(normalized)), key=lambda i: normalized[i])
    peak_value = y[peak_index]
    overshoot = max(0, (normalized[peak_index] - 1) * 100)
    peak_time = time[peak_index] if overshoot > 1e-6 else None

    band = 0.02 * abs(final_value)
    last_outside = None

    for i, value in enumerate(y):
        if abs(value - final_value) > band:
            last_outside = i

    if last_outside is None:
        settling_time = 0.0
    elif last_outside >= len(y) - 1:
        settling_time = None
    else:
        settling_time = time[last_outside + 1]

    return {
        "rise_time": rise_time,
        "peak_time": peak_time,
        "peak_value": peak_value,
        "overshoot_percent": overshoot,
        "settling_time": settling_time
    }


def dashboard_json(zeta, wn, gain=1.0, step=1.0):
    dt, end_time = simulation_settings(zeta, wn)

    # Required closed-form response
    time, position, velocity = closed_form_response(zeta, wn, gain, step, dt, end_time)

    # Bonus: RK4 numerical response for comparison
    A = [[0, 1], [-(wn ** 2), -2 * zeta * wn]]
    B = [0, gain * wn ** 2]
    rk4_time, rk4_position, _ = rk4(A, B, step, dt, end_time)

    final_value = gain * step
    response_metrics = metrics(time, position, final_value)

    result = {
        "zeta": zeta,
        "omega_n": wn,
        "gain": gain,
        "step_amplitude": step,
        "damping_type": damping_type(zeta),
        "poles": poles(zeta, wn),
        "time": time,
        "position": position,
        "velocity": velocity,
        "rk4_time": rk4_time,
        "rk4_position": rk4_position,
        **response_metrics,
        "final_value": final_value,
        "dt": dt,
        "end_time": end_time,
        "response_method": "closed-form + RK4 comparison"
    }

    return json.dumps(result, allow_nan=False)


def physical_dashboard_json(mass, b, k, force=1.0):
    wn, zeta, A, B = physical_values(mass, b, k)

    dt, end_time = simulation_settings(zeta, wn)
    time, position, velocity = closed_form_response(zeta, wn, 1 / k, force, dt, end_time)

    final_value = force / k
    response_metrics = metrics(time, position, final_value)

    result = {
        "m": mass,
        "b": b,
        "k": k,
        "force": force,
        "omega_n": wn,
        "zeta": zeta,
        "damping_type": damping_type(zeta),
        "A": A,
        "B": B,
        "poles": poles(zeta, wn),
        "eigenvalues": eigenvalues(A),
        "time": time,
        "position": position,
        "velocity": velocity,
        **response_metrics,
        "final_value": final_value,
        "dt": dt,
        "end_time": end_time,
        "response_method": "closed-form"
    }

    return json.dumps(result, allow_nan=False)


def validation_json():
    test1 = json.loads(dashboard_json(0.5, 2))
    test2 = json.loads(dashboard_json(1.0, 2))

    wn, zeta, A, _ = physical_values(1, 2, 4)
    eig = eigenvalues(A)
    system_poles = poles(zeta, wn)

    physical_pass = (
        abs(wn - 2.0) <= 0.001
        and abs(zeta - 0.5) <= 0.001
        and abs(eig[0]["re"] - system_poles[0]["re"]) <= 0.001
        and abs(eig[0]["im"] - system_poles[0]["im"]) <= 0.001
        and abs(eig[1]["re"] - system_poles[1]["re"]) <= 0.001
        and abs(eig[1]["im"] - system_poles[1]["im"]) <= 0.001
    )

    checks = [
        {
            "test": "zeta = 0.5 overshoot",
            "expected": 16.3,
            "actual": test1["overshoot_percent"],
            "passed": abs(test1["overshoot_percent"] - 16.3) <= 0.1
        },
        {
            "test": "zeta = 1 overshoot",
            "expected": 0,
            "actual": test2["overshoot_percent"],
            "passed": abs(test2["overshoot_percent"]) <= 0.01
        },
        {
            "test": "m=1, b=2, k=4",
            "expected": {
                "omega_n": 2.0,
                "zeta": 0.5,
                "eigenvalues": "-1 +/- j1.732"
            },
            "actual": {
                "omega_n": wn,
                "zeta": zeta,
                "eigenvalues": eig
            },
            "passed": physical_pass
        }
    ]

    return json.dumps(checks, allow_nan=False)


if __name__ == "__main__":
    print("Homework validation")
    print(validation_json())

    print()

    overdamped = json.loads(dashboard_json(2.0, 2.0))

    print("Overdamped test")
    print("settling_time:", overdamped["settling_time"])

    print()

    small_zeta = json.loads(dashboard_json(0.05, 2.0))

    print("Small zeta test")
    print("points:", len(small_zeta["time"]))
    print("settling_time:", small_zeta["settling_time"])

    print()

    zero_gain = json.loads(dashboard_json(0.5, 2.0, gain=0.0))

    print("Zero gain test")
    print("rise_time:", zero_gain["rise_time"])
    print("overshoot:", zero_gain["overshoot_percent"])