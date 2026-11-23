
"""ENCS4380 Homework 2 — State-Space Pole Placement bonus.

Mass-spring-damper model from Homework 1 Module 3:
    m*x'' + b*x' + k*x = u

State feedback:
    u = -K1*x - K2*v

This module implements pole placement and numerical RK4 simulation.
"""

import json
import math


def validate_parameters(m, b, k, zeta, wn, x0, v0, duration):
    values = (m, b, k, zeta, wn, x0, v0, duration)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("All parameters must be finite numbers.")
    if m <= 0 or k <= 0 or b < 0:
        raise ValueError("Require m > 0, k > 0 and b >= 0.")
    if zeta <= 0 or wn <= 0:
        raise ValueError("Desired zeta and omega_n must be positive.")
    if duration <= 0 or duration > 120:
        raise ValueError("Duration must be between 0 and 120 seconds.")


def eigenvalues(a):
    trace = a[0][0] + a[1][1]
    determinant = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    discriminant = complex(trace * trace - 4 * determinant, 0)
    root = discriminant ** 0.5
    return [
        (trace + root) / 2,
        (trace - root) / 2,
    ]


def pole_placement(m, b, k, zeta, wn):
    """Calculate gains for the desired characteristic polynomial."""
    k1 = m * wn**2 - k
    k2 = 2 * m * zeta * wn - b

    a = [[0.0, 1.0], [-k / m, -b / m]]
    b_matrix = [[0.0], [1.0 / m]]

    a_closed = [
        [0.0, 1.0],
        [-(k + k1) / m, -(b + k2) / m],
    ]

    return {
        "K1": k1,
        "K2": k2,
        "A": a,
        "B": b_matrix,
        "A_closed": a_closed,
        "open_poles": eigenvalues(a),
        "closed_poles": eigenvalues(a_closed),
    }


def rk4_simulation(m, b, k, k1, k2, x0, v0, duration, steps=2000):
    """Integrate the physical system with fourth-order Runge-Kutta."""
    dt = duration / steps
    state = [x0, v0]

    time = [0.0]
    position = [x0]
    velocity = [v0]
    control = [-k1 * x0 - k2 * v0]

    def derivative(s):
        x, v = s
        u = -k1 * x - k2 * v
        return [v, (u - b * v - k * x) / m]

    for i in range(steps):
        a1 = derivative(state)
        s2 = [state[j] + dt * a1[j] / 2 for j in range(2)]
        a2 = derivative(s2)
        s3 = [state[j] + dt * a2[j] / 2 for j in range(2)]
        a3 = derivative(s3)
        s4 = [state[j] + dt * a3[j] for j in range(2)]
        a4 = derivative(s4)

        state = [
            state[j] + dt * (
                a1[j] + 2 * a2[j] + 2 * a3[j] + a4[j]
            ) / 6
            for j in range(2)
        ]

        time.append((i + 1) * dt)
        position.append(state[0])
        velocity.append(state[1])
        control.append(-k1 * state[0] - k2 * state[1])

    return {
        "time": time,
        "position": position,
        "velocity": velocity,
        "control": control,
    }


def dashboard_json(
    m=1.0,
    b=2.0,
    k=4.0,
    zeta=0.7,
    wn=3.0,
    x0=1.0,
    v0=0.0,
    duration=12.0,
):
    validate_parameters(m, b, k, zeta, wn, x0, v0, duration)

    design = pole_placement(m, b, k, zeta, wn)

    open_response = rk4_simulation(
        m, b, k, 0.0, 0.0, x0, v0, duration
    )

    closed_response = rk4_simulation(
        m, b, k, design["K1"], design["K2"], x0, v0, duration
    )

    def serialize_poles(poles):
        return [
            {"re": pole.real, "im": pole.imag}
            for pole in poles
        ]

    return json.dumps({
        "parameters": {
            "m": m, "b": b, "k": k,
            "zeta": zeta, "omega_n": wn,
            "x0": x0, "v0": v0,
            "duration": duration,
        },
        "K1": design["K1"],
        "K2": design["K2"],
        "A": design["A"],
        "B": design["B"],
        "A_closed": design["A_closed"],
        "open_poles": serialize_poles(design["open_poles"]),
        "closed_poles": serialize_poles(design["closed_poles"]),
        "open_response": open_response,
        "closed_response": closed_response,
        "method": "RK4",
        "control_law": "u = -K1*x - K2*v",
    }, allow_nan=False)


if __name__ == "__main__":
    result = json.loads(dashboard_json())
    print("STATE-SPACE POLE PLACEMENT")
    print("K1 =", result["K1"])
    print("K2 =", result["K2"])
    print("Open-loop poles =", result["open_poles"])
    print("Closed-loop poles =", result["closed_poles"])
    print("Simulation points =", len(result["closed_response"]["time"]))
