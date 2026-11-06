"""Module 3: Second-order response model for the ENCS4380 toolkit."""

from math import sqrt, pi, isfinite
import json


# ------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------

def require_positive(**values):
    """Require every supplied value to be finite and greater than zero."""
    for name, value in values.items():
        if not isfinite(value) or value <= 0:
            raise ValueError(
                name + " must be a finite number greater than zero."
            )


def require_nonnegative(**values):
    """Require every supplied value to be finite and >= 0."""
    for name, value in values.items():
        if not isfinite(value) or value < 0:
            raise ValueError(
                name + " must be a finite number greater than or equal to zero."
            )


# ------------------------------------------------------------
# Damping type and poles
# ------------------------------------------------------------

def damping_type(zeta):
    """Classify the second-order response using zeta."""
    require_nonnegative(zeta=zeta)

    if abs(zeta - 1.0) < 1e-9:
        return "Critically damped"

    if zeta < 1.0:
        return "Underdamped"

    return "Overdamped"


def poles(zeta, omega_n):
    """Return the two poles of the standard second-order system."""
    require_nonnegative(zeta=zeta)
    require_positive(omega_n=omega_n)

    real_part = -zeta * omega_n

    # Underdamped: complex-conjugate poles.
    if zeta < 1.0:
        imag_part = omega_n * sqrt(1.0 - zeta * zeta)

        return [
            {"re": real_part, "im": imag_part},
            {"re": real_part, "im": -imag_part},
        ]

    # Critically damped: repeated real pole.
    if abs(zeta - 1.0) < 1e-9:
        return [
            {"re": -omega_n, "im": 0.0},
            {"re": -omega_n, "im": 0.0},
        ]

    # Overdamped: two different negative real poles.
    root = omega_n * sqrt(zeta * zeta - 1.0)

    return [
        {"re": real_part + root, "im": 0.0},
        {"re": real_part - root, "im": 0.0},
    ]


# ------------------------------------------------------------
# State-space matrices
# ------------------------------------------------------------

def second_order_matrices(zeta, omega_n, gain=1.0):
    """
    Standard second-order model:

        G(s) = K*wn^2 / (s^2 + 2*zeta*wn*s + wn^2)

    States:
        x1 = y
        x2 = y_dot
    """
    require_nonnegative(zeta=zeta)
    require_positive(omega_n=omega_n)

    if not isfinite(gain):
        raise ValueError("gain must be finite.")

    A = [
        [0.0, 1.0],
        [-(omega_n ** 2), -2.0 * zeta * omega_n],
    ]

    B = [
        0.0,
        gain * (omega_n ** 2),
    ]

    return A, B


def physical_parameters(m, b, k):
    """Convert mass-spring-damper parameters into omega_n and zeta."""
    require_positive(m=m, k=k)
    require_nonnegative(b=b)

    omega_n = sqrt(k / m)
    zeta = b / (2.0 * sqrt(k * m))

    return {
        "omega_n": omega_n,
        "zeta": zeta,
    }


def physical_state_space(m, b, k):
    """
    Mass-spring-damper model:

        m*x_ddot + b*x_dot + k*x = F

    States:
        x1 = position
        x2 = velocity
    """
    require_positive(m=m, k=k)
    require_nonnegative(b=b)

    A = [
        [0.0, 1.0],
        [-k / m, -b / m],
    ]

    B = [
        0.0,
        1.0 / m,
    ]

    return A, B


# ------------------------------------------------------------
# Eigenvalues
# ------------------------------------------------------------

def eigenvalues_2x2(A):
    """Return the two eigenvalues of a 2x2 matrix."""
    trace = A[0][0] + A[1][1]

    determinant = (
        A[0][0] * A[1][1]
        - A[0][1] * A[1][0]
    )

    discriminant = trace * trace / 4.0 - determinant

    if discriminant >= 0:
        root = sqrt(discriminant)

        return [
            {
                "re": trace / 2.0 + root,
                "im": 0.0,
            },
            {
                "re": trace / 2.0 - root,
                "im": 0.0,
            },
        ]

    imag = sqrt(-discriminant)

    return [
        {
            "re": trace / 2.0,
            "im": imag,
        },
        {
            "re": trace / 2.0,
            "im": -imag,
        },
    ]


# ------------------------------------------------------------
# Adaptive simulation settings
# ------------------------------------------------------------

def simulation_settings(zeta, omega_n):
    """
    Choose simulation duration and RK4 step size from the system poles.

    Settling time is based on the slow dynamics.
    Integration step is based on the fastest dynamics.
    """
    require_nonnegative(zeta=zeta)
    require_positive(omega_n=omega_n)

    # Overdamped:
    # use the slow pole for settling and the fast pole for dt.
    if zeta > 1.0 + 1e-9:
        root = sqrt(zeta * zeta - 1.0)

        slow = omega_n / (zeta + root)
        fast = omega_n * (zeta + root)

        estimated_settling = 4.0 / slow

    # Critically damped.
    elif zeta >= 1.0 - 1e-9:
        fast = omega_n

        # Approximate 2% settling time for the critical case.
        estimated_settling = 5.83 / omega_n

    # Underdamped.
    elif zeta > 0:
        fast = omega_n
        estimated_settling = 4.0 / (zeta * omega_n)

    # Undamped system never settles.
    else:
        dt = 1.0 / (40.0 * omega_n)
        end_time = 10.0 * pi / omega_n

        return dt, end_time

    end_time = max(
        10.0 / omega_n,
        1.5 * estimated_settling,
    )

    dt = min(
        0.01,
        1.0 / (40.0 * fast),
    )

    return dt, end_time


# ------------------------------------------------------------
# Generic RK4 state-space simulator
# ------------------------------------------------------------

def simulate_rk4(
    A,
    B,
    input_value,
    x0,
    dt,
    end_time,
):
    """Simulate dx/dt = A*x + B*u using fourth-order Runge-Kutta."""
    require_positive(dt=dt, end_time=end_time)

    x = list(x0)

    times = [0.0]
    states = [x.copy()]

    # Fixed step count avoids floating-point accumulation
    # from repeatedly doing t += dt.
    steps = max(
        1,
        round(end_time / dt),
    )

    def derivative(state):
        """Compute dx/dt = A*x + B*u."""
        result = []

        for i in range(len(state)):
            value = 0.0

            for j in range(len(state)):
                value += A[i][j] * state[j]

            value += B[i] * input_value

            result.append(value)

        return result

    for step in range(steps):
        k1 = derivative(x)

        state2 = [
            x[i] + 0.5 * dt * k1[i]
            for i in range(len(x))
        ]
        k2 = derivative(state2)

        state3 = [
            x[i] + 0.5 * dt * k2[i]
            for i in range(len(x))
        ]
        k3 = derivative(state3)

        state4 = [
            x[i] + dt * k3[i]
            for i in range(len(x))
        ]
        k4 = derivative(state4)

        x = [
            x[i]
            + dt / 6.0
            * (
                k1[i]
                + 2.0 * k2[i]
                + 2.0 * k3[i]
                + k4[i]
            )
            for i in range(len(x))
        ]

        t = (step + 1) * dt

        times.append(t)
        states.append(x.copy())

    return {
        "time": times,
        "states": states,
    }


# ------------------------------------------------------------
# Standard second-order simulation
# ------------------------------------------------------------

def standard_step_response(
    zeta,
    omega_n,
    gain=1.0,
    step_amplitude=1.0,
):
    """Simulate the standard second-order step response."""
    require_nonnegative(zeta=zeta)
    require_positive(omega_n=omega_n)

    if not isfinite(gain) or not isfinite(step_amplitude):
        raise ValueError(
            "gain and step amplitude must be finite."
        )

    A, B = second_order_matrices(
        zeta,
        omega_n,
        gain,
    )

    dt, end_time = simulation_settings(
        zeta,
        omega_n,
    )

    simulation = simulate_rk4(
        A=A,
        B=B,
        input_value=step_amplitude,
        x0=[0.0, 0.0],
        dt=dt,
        end_time=end_time,
    )

    position = [
        state[0]
        for state in simulation["states"]
    ]

    velocity = [
        state[1]
        for state in simulation["states"]
    ]

    return {
        "time": simulation["time"],
        "position": position,
        "velocity": velocity,
        "dt": dt,
        "end_time": end_time,
    }


# ------------------------------------------------------------
# Physical mass-spring-damper simulation
# ------------------------------------------------------------

def physical_step_response(
    m,
    b,
    k,
    force=1.0,
):
    """Simulate the mass-spring-damper directly using m, b and k."""
    require_positive(m=m, k=k)
    require_nonnegative(b=b)

    if not isfinite(force):
        raise ValueError("force must be finite.")

    params = physical_parameters(
        m,
        b,
        k,
    )

    omega_n = params["omega_n"]
    zeta = params["zeta"]

    A, B = physical_state_space(
        m,
        b,
        k,
    )

    dt, end_time = simulation_settings(
        zeta,
        omega_n,
    )

    simulation = simulate_rk4(
        A=A,
        B=B,
        input_value=force,
        x0=[0.0, 0.0],
        dt=dt,
        end_time=end_time,
    )

    position = [
        state[0]
        for state in simulation["states"]
    ]

    velocity = [
        state[1]
        for state in simulation["states"]
    ]

    return {
        "time": simulation["time"],
        "position": position,
        "velocity": velocity,
        "dt": dt,
        "end_time": end_time,
    }


# ------------------------------------------------------------
# Curve measurement helpers
# ------------------------------------------------------------

def interpolated_crossing_time(
    t1,
    y1,
    t2,
    y2,
    target,
):
    """Linearly interpolate the time at which a curve crosses target."""
    if y2 == y1:
        return t2

    fraction = (
        (target - y1)
        / (y2 - y1)
    )

    return (
        t1
        + fraction * (t2 - t1)
    )


def rise_time_from_curve(
    times,
    values,
    final_value,
):
    """Measure the 10%-to-90% rise time from the simulated curve."""
    if final_value == 0:
        return None

    # Normalize the response relative to its final value.
    normalized = [
        value / final_value
        for value in values
    ]

    crossing_times = {}

    for target in (0.1, 0.9):
        for i in range(1, len(normalized)):
            y1 = normalized[i - 1]
            y2 = normalized[i]

            if y1 < target <= y2:
                crossing_times[target] = interpolated_crossing_time(
                    times[i - 1],
                    y1,
                    times[i],
                    y2,
                    target,
                )
                break

    if 0.1 not in crossing_times or 0.9 not in crossing_times:
        return None

    return (
        crossing_times[0.9]
        - crossing_times[0.1]
    )


def peak_metrics_from_curve(
    times,
    values,
    final_value,
):
    """Measure peak value, peak time and overshoot from the curve."""
    if final_value == 0:
        return {
            "peak_time": None,
            "peak_value": None,
            "overshoot_percent": None,
        }

    normalized = [
        value / final_value
        for value in values
    ]

    peak_index = max(
        range(len(normalized)),
        key=lambda i: normalized[i],
    )

    peak_ratio = normalized[peak_index]

    overshoot = max(
        0.0,
        (peak_ratio - 1.0) * 100.0,
    )

    # Critical and overdamped systems have no overshoot peak.
    if overshoot <= 1e-6:
        peak_time = None
    else:
        peak_time = times[peak_index]

    return {
        "peak_time": peak_time,
        "peak_value": values[peak_index],
        "overshoot_percent": overshoot,
    }


def settling_time_from_curve(
    times,
    values,
    final_value,
    tolerance=0.02,
):
    """Measure settling time using a +/-2% band."""
    if final_value == 0:
        return None

    band = tolerance * abs(final_value)

    last_outside = None

    for i, value in enumerate(values):
        if abs(value - final_value) > band:
            last_outside = i

    if last_outside is None:
        return 0.0

    if last_outside >= len(values) - 1:
        return None

    return times[last_outside + 1]


def response_metrics(
    times,
    values,
    final_value,
):
    """Measure all required Module 3 response metrics from the curve."""
    peak = peak_metrics_from_curve(
        times,
        values,
        final_value,
    )

    return {
        "rise_time": rise_time_from_curve(
            times,
            values,
            final_value,
        ),

        "peak_time": peak["peak_time"],

        "peak_value": peak["peak_value"],

        "overshoot_percent": peak[
            "overshoot_percent"
        ],

        "settling_time": settling_time_from_curve(
            times,
            values,
            final_value,
        ),
    }


# ------------------------------------------------------------
# JSON dashboard: zeta and omega_n
# ------------------------------------------------------------

def dashboard_json(
    zeta,
    omega_n,
    gain=1.0,
    step_amplitude=1.0,
):
    """Return live second-order response data for module-3.html."""
    response = standard_step_response(
        zeta,
        omega_n,
        gain,
        step_amplitude,
    )

    final_value = (
        gain * step_amplitude
    )

    metrics = response_metrics(
        response["time"],
        response["position"],
        final_value,
    )

    result = {
        "zeta": zeta,
        "omega_n": omega_n,
        "gain": gain,
        "step_amplitude": step_amplitude,

        "damping_type": damping_type(
            zeta
        ),

        "poles": poles(
            zeta,
            omega_n,
        ),

        "time": response["time"],
        "position": response["position"],
        "velocity": response["velocity"],

        "rise_time": metrics["rise_time"],
        "peak_time": metrics["peak_time"],
        "peak_value": metrics["peak_value"],
        "overshoot_percent": metrics[
            "overshoot_percent"
        ],
        "settling_time": metrics[
            "settling_time"
        ],

        "final_value": final_value,

        "dt": response["dt"],
        "end_time": response["end_time"],
    }

    return json.dumps(
        result,
        allow_nan=False,
    )


# ------------------------------------------------------------
# JSON dashboard: physical m, b, k model
# ------------------------------------------------------------

def physical_dashboard_json(
    m,
    b,
    k,
    force=1.0,
):
    """Return live mass-spring-damper state-space data."""
    params = physical_parameters(
        m,
        b,
        k,
    )

    omega_n = params["omega_n"]
    zeta = params["zeta"]

    A, B = physical_state_space(
        m,
        b,
        k,
    )

    eigenvalues = eigenvalues_2x2(A)

    response = physical_step_response(
        m,
        b,
        k,
        force,
    )

    # At steady state:
    # k*x = F  ->  x = F/k
    final_value = force / k

    metrics = response_metrics(
        response["time"],
        response["position"],
        final_value,
    )

    result = {
        "m": m,
        "b": b,
        "k": k,
        "force": force,

        "omega_n": omega_n,
        "zeta": zeta,

        "damping_type": damping_type(
            zeta
        ),

        "A": A,
        "B": B,

        "eigenvalues": eigenvalues,

        "poles": poles(
            zeta,
            omega_n,
        ),

        "time": response["time"],
        "position": response["position"],
        "velocity": response["velocity"],

        "rise_time": metrics["rise_time"],
        "peak_time": metrics["peak_time"],
        "peak_value": metrics["peak_value"],
        "overshoot_percent": metrics[
            "overshoot_percent"
        ],
        "settling_time": metrics[
            "settling_time"
        ],

        "final_value": final_value,

        "dt": response["dt"],
        "end_time": response["end_time"],
    }

    return json.dumps(
        result,
        allow_nan=False,
    )


# ------------------------------------------------------------
# Required homework validation
# ------------------------------------------------------------

def validation_json():
    """Return the Module 3 validation checks required by the homework."""

    # Check 1: zeta = 0.5 -> overshoot approximately 16.3%.
    response_half = standard_step_response(
        zeta=0.5,
        omega_n=2.0,
    )

    metrics_half = response_metrics(
        response_half["time"],
        response_half["position"],
        1.0,
    )

    measured_overshoot = metrics_half[
        "overshoot_percent"
    ]

    overshoot_pass = (
        abs(measured_overshoot - 16.3)
        <= 0.1
    )

    # Check 2: zeta = 1 -> no overshoot.
    response_critical = standard_step_response(
        zeta=1.0,
        omega_n=2.0,
    )

    metrics_critical = response_metrics(
        response_critical["time"],
        response_critical["position"],
        1.0,
    )

    critical_overshoot = metrics_critical[
        "overshoot_percent"
    ]

    critical_pass = (
        abs(critical_overshoot)
        <= 0.01
    )

    # Check 3: m = 1, b = 2, k = 4.
    m = 1.0
    b = 2.0
    k = 4.0

    params = physical_parameters(
        m,
        b,
        k,
    )

    A, _ = physical_state_space(
        m,
        b,
        k,
    )

    eig = eigenvalues_2x2(A)

    system_poles = poles(
        params["zeta"],
        params["omega_n"],
    )

    omega_pass = (
        abs(params["omega_n"] - 2.0)
        <= 0.001
    )

    zeta_pass = (
        abs(params["zeta"] - 0.5)
        <= 0.001
    )

    eigenvalue_pass = (
        abs(
            eig[0]["re"]
            - system_poles[0]["re"]
        ) <= 0.001

        and abs(
            eig[0]["im"]
            - system_poles[0]["im"]
        ) <= 0.001

        and abs(
            eig[1]["re"]
            - system_poles[1]["re"]
        ) <= 0.001

        and abs(
            eig[1]["im"]
            - system_poles[1]["im"]
        ) <= 0.001
    )

    result = [
        {
            "test": "zeta = 0.5 overshoot",
            "expected": 16.3,
            "actual": measured_overshoot,
            "unit": "%",
            "passed": overshoot_pass,
        },
        {
            "test": "zeta = 1 overshoot",
            "expected": 0.0,
            "actual": critical_overshoot,
            "unit": "%",
            "passed": critical_pass,
        },
        {
            "test": "m=1, b=2, k=4 natural frequency",
            "expected": 2.0,
            "actual": params["omega_n"],
            "unit": "rad/s",
            "passed": omega_pass,
        },
        {
            "test": "m=1, b=2, k=4 damping ratio",
            "expected": 0.5,
            "actual": params["zeta"],
            "unit": "",
            "passed": zeta_pass,
        },
        {
            "test": "Eigenvalues match poles",
            "expected": "-1 +/- j1.732",
            "actual": eig,
            "unit": "",
            "passed": eigenvalue_pass,
        },
    ]

    return json.dumps(
        result,
        allow_nan=False,
    )


# ------------------------------------------------------------
# Local tests
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Module 3 test")
    print()

    print("Standard model: zeta=0.5, omega_n=2")
    print(dashboard_json(0.5, 2.0))
    print()

    print("Physical model: m=1, b=2, k=4, F=4")
    print(
        physical_dashboard_json(
            1.0,
            2.0,
            4.0,
            4.0,
        )
    )
    print()

    print("Homework validation")
    print(validation_json())
    print()

    # Extra check for the overdamped simulation duration.
    overdamped_test = json.loads(
        dashboard_json(
            2.0,
            2.0,
        )
    )

    print("Overdamped test: zeta=2, omega_n=2")
    print(
        "end_time:",
        overdamped_test["end_time"],
    )
    print(
        "settling_time:",
        overdamped_test["settling_time"],
    )
