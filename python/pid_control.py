"""Homework 2 - P1 PID Playground
First-order plant with PID feedback control.

Plant:
    tau * dy/dt + y = K * u

PID controller:
    e = setpoint - y
    P = Kp * e
    I = Ki * integral(e)
    D = -Kd * filtered(dy/dt)
    u = P + I + D

"""


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def simulate_pid_control(K=1.0, tau=1.0, Kp=1.0, Ki=0.0, Kd=0.0, setpoint=1.0, u_min=-100.0, u_max=100.0, dt=0.001, duration=8.0, anti_windup=True):
    if tau <= 0: raise ValueError("tau must be greater than zero.")

    if dt <= 0: raise ValueError("dt must be greater than zero.")

    if duration <= 0: raise ValueError("duration must be greater than zero.")

    if u_min >= u_max: raise ValueError("u_min must be smaller than u_max.")

    time = []
    output = []
    control = []
    error_values = []

    p_values = []
    i_values = []
    d_values = []

    saturation_values = []

    # Initial conditions
    y = 0.0
    integral = 0.0

    # Start with the current output so the derivative term is zero
    # at the first simulation step.
    previous_output = y
    filtered_derivative = 0.0
    derivative_filter_alpha = 0.15
    steps = int(duration / dt) + 1

    for i in range(steps):
        t = i * dt

        # -----------------------------------
        # 1. Error
        # -----------------------------------
        error = setpoint - y

        # -----------------------------------
        # 2. P term
        # -----------------------------------
        p_term = Kp * error

        # -----------------------------------
        # 3. D term
        # -----------------------------------

        measurement_derivative = (y - previous_output) / dt

        # Low-pass filter for the derivative term
        filtered_derivative = derivative_filter_alpha * measurement_derivative + (1.0 - derivative_filter_alpha) * filtered_derivative

        d_term = -Kd * filtered_derivative

        # -----------------------------------
        # 4. Candidate Integral
        # -----------------------------------
        # Do not immediately save it.
        # First check whether it would create
        # more actuator saturation.
        candidate_integral = integral + error * dt

        candidate_i_term = Ki * candidate_integral

        candidate_u = p_term + candidate_i_term + d_term

        # -----------------------------------
        # 5. Anti-windup decision
        # -----------------------------------

        if anti_windup:

            pushing_above_upper_limit = (candidate_u > u_max and error > 0)

            pushing_below_lower_limit = (candidate_u < u_min and error < 0)

            if not (pushing_above_upper_limit or pushing_below_lower_limit):
                # Integral is allowed to update
                integral = candidate_integral

        else:
            # No anti-windup:
            # always allow the integral to grow
            integral = candidate_integral

        # Final I term after anti-windup decision
        i_term = Ki * integral

        # -----------------------------------
        # 6. PID output before actuator limit
        # -----------------------------------
        u_unsaturated = p_term + i_term + d_term

        # -----------------------------------
        # 7. Apply actuator saturation
        # -----------------------------------
        u = clamp(u_unsaturated, u_min, u_max)

        saturated = (u != u_unsaturated)

        # -----------------------------------
        # 8. First-order plant
        # tau * dy/dt + y = K*u
        # -----------------------------------
        dydt = (K * u - y) / tau

        # -----------------------------------
        # 9. Euler update
        # -----------------------------------
        # Save the current output before advancing the plant.
        # On the next iteration this lets us calculate dy/dt correctly.
        previous_output = y
        y = y + dydt * dt

        # -----------------------------------
        # 10. Save values
        # -----------------------------------
        time.append(t)
        output.append(y)
        control.append(u)
        error_values.append(error)

        p_values.append(p_term)
        i_values.append(i_term)
        d_values.append(d_term)

        saturation_values.append(saturated)

    return {
        "time": time, "output": output, "control": control, "error": error_values,

        "p_term": p_values, "i_term": i_values, "d_term": d_values,

        "saturated": saturation_values,

        "final_output": output[-1], "final_error": setpoint - output[-1],

        "anti_windup": anti_windup, "u_min": u_min, "u_max": u_max
    }


def p_validation_check():
    """
    Validation 1:
    K = 1
    tau = 1
    Kp = 9
    Ki = 0
    Kd = 0

    Expected:
    closed-loop tau = 0.1 s
    steady-state error = 10%
    """

    K = 1.0
    tau = 1.0
    Kp = 9.0
    setpoint = 1.0

    result = simulate_pid_control(K=K, tau=tau, Kp=Kp, Ki=0.0, Kd=0.0, setpoint=setpoint, duration=2.0)

    closed_loop_tau = tau / (1.0 + K * Kp)

    theoretical_final_output = (K * Kp / (1.0 + K * Kp)) * setpoint

    theoretical_error = setpoint - theoretical_final_output

    theoretical_error_percent = (abs(theoretical_error) / abs(setpoint)) * 100.0

    simulated_error_percent = (abs(result["final_error"]) / abs(setpoint)) * 100.0

    return {"closed_loop_tau": closed_loop_tau, "theoretical_error_percent": theoretical_error_percent, "simulated_final_output": result["final_output"], "simulated_error_percent": simulated_error_percent}


def pi_validation_check():
    """
    Validation 2:
    K = 1
    tau = 1
    Kp = 1
    Ki = 1
    Kd = 0

    Expected:
    omega_n = 1 rad/s
    zeta = 1
    steady-state error = 0
    """

    K = 1.0
    tau = 1.0
    Kp = 1.0
    Ki = 1.0
    setpoint = 1.0

    result = simulate_pid_control(K=K, tau=tau, Kp=Kp, Ki=Ki, Kd=0.0, setpoint=setpoint, duration=10.0)

    omega_n = (K * Ki / tau) ** 0.5

    zeta = (1.0 + K * Kp) / (2.0 * (tau * K * Ki) ** 0.5)

    steady_state_error_percent = (abs(result["final_error"]) / abs(setpoint)) * 100.0

    return {"omega_n": omega_n, "zeta": zeta, "simulated_final_output": result["final_output"], "steady_state_error_percent": steady_state_error_percent}

def calculate_metrics(time, output, setpoint):
    """
    Calculate:
    - Rise time: 10% to 90% of setpoint
    - Overshoot percentage
    - Settling time: ±2% band
    - Steady-state error percentage
    """

    if setpoint == 0:
        return {"rise_time": None, "overshoot_percent": 0.0, "settling_time": None, "steady_state_error_percent": 0.0}

    final_output = output[-1]

    # -------------------------
    # 1. Rise Time
    # -------------------------
    level_10 = 0.1 * setpoint
    level_90 = 0.9 * setpoint

    t10 = None
    t90 = None

    for t, y in zip(time, output):
        if t10 is None and y >= level_10:
            t10 = t

        if t90 is None and y >= level_90:
            t90 = t
            break

    rise_time = None

    if t10 is not None and t90 is not None:
        rise_time = t90 - t10

    # -------------------------
    # 2. Overshoot
    # -------------------------
    peak_output = max(output)

    overshoot_percent = max(0.0, ((peak_output - setpoint) / abs(setpoint)) * 100.0)

    # -------------------------
    # 3. Settling Time
    # -------------------------
    tolerance = 0.02 * abs(setpoint)

    lower_limit = setpoint - tolerance
    upper_limit = setpoint + tolerance

    settling_time = None

    for i in range(len(output)):
        remaining_output = output[i:]

        if all(lower_limit <= y <= upper_limit for y in remaining_output):
            settling_time = time[i]
            break

    # -------------------------
    # 4. Steady-State Error
    # -------------------------
    steady_state_error_percent = (abs(setpoint - final_output) / abs(setpoint)) * 100.0

    return {"rise_time": rise_time, "overshoot_percent": overshoot_percent, "settling_time": settling_time, "steady_state_error_percent": steady_state_error_percent}


def pid_demo():
    """
    PID example with response metrics.
    """

    setpoint = 1.0

    result = simulate_pid_control(K=1.0, tau=1.0, Kp=2.0, Ki=1.0, Kd=0.5, setpoint=setpoint, duration=8.0)

    metrics = calculate_metrics(result["time"], result["output"], setpoint)

    return {"final_output": result["final_output"], "final_error": result["final_error"], "max_output": max(result["output"]), "max_control": max(result["control"]), "min_control": min(result["control"]), **metrics}


if __name__ == "__main__":

    print("P1 - Validation 1: P Controller")
    print("-------------------------------")

    p_check = p_validation_check()

    print("Closed-loop time constant:", round(p_check["closed_loop_tau"], 4), "s")

    print("Expected steady-state error:", round(p_check["theoretical_error_percent"], 4), "%")

    print("Simulated final output:", round(p_check["simulated_final_output"], 4))

    print("Simulated steady-state error:", round(p_check["simulated_error_percent"], 4), "%")

    print()

    print("P1 - Validation 2: PI Controller")
    print("--------------------------------")

    pi_check = pi_validation_check()

    print("Natural frequency omega_n:", round(pi_check["omega_n"], 4), "rad/s")

    print("Damping ratio zeta:", round(pi_check["zeta"], 4))

    print("Simulated final output:", round(pi_check["simulated_final_output"], 4))

    print("Simulated steady-state error:", round(pi_check["steady_state_error_percent"], 4), "%")

    print()

    print("P1 - PID Demo")
    print("-------------")

    demo = pid_demo()

    print("Final output:", round(demo["final_output"], 4))

    print("Final error:", round(demo["final_error"], 6))

    print("Maximum output:", round(demo["max_output"], 4))

    print("Control range:", round(demo["min_control"], 4), "to", round(demo["max_control"], 4))

    print("Rise time:", None if demo["rise_time"] is None else round(demo["rise_time"], 4), "s")

    print("Overshoot:", round(demo["overshoot_percent"], 4), "%")

    print("Settling time:", None if demo["settling_time"] is None else round(demo["settling_time"], 4), "s")

    print("Steady-state error:", round(demo["steady_state_error_percent"], 4), "%")
