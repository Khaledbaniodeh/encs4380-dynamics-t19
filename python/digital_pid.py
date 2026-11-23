"""Homework 2 / P3 Stage 2 — sampled PID on a first-order plant.

CONTROLLER: changes at t = k*Ts (discrete-time).
  e[k] = r - y(k*Ts)
  P[k] = Kp * e[k]
  I_candidate[k] = I[k-1] + Ki * Ts * e[k]
  D[k] = Kd * (e[k] - e[k-1]) / Ts
  u_raw[k] = P[k] + I[k] + D[k]
  u[k] = clip(u_raw[k], u_min, u_max)

First sample: e[-1] is initialized to e[0], so D[0]=0 (no startup kick).
Integral starts at 0 *before* sample 0, and includes e[0] at sample 0.
Optional anti-windup uses conditional integration (freeze only if the proposed
integral pushes farther into actuator saturation). This is a chosen design,
not an extra mathematical requirement imposed by the assignment.

PLANT: still continuous-time, stepped using forward Euler with h << Ts:
  tau * dy/dt + y = K*u
  y_next = y + h * (K*u - y) / tau
Between controller samples, u is held constant (zero-order hold).

This is a local learning prototype. It is not a calibrated motor/PWM model,
not a final Arduino implementation, and not the final P3 submission.
"""
import json
import math


def _finite(label, value):
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{label} must be a number.") from None
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite.")
    return number


def _crossing_time(times, values, level):
    for i in range(1, len(times)):
        low, high = values[i-1], values[i]
        if low < level <= high:
            return times[i-1] + (level-low)/(high-low)*(times[i]-times[i-1])
    return None


def simulate_pid(K=1.0, tau=1.0, Kp=2.0, Ki=0.0, Kd=0.0,
                 Ts=0.2, setpoint=1.0, duration=5.0,
                 u_min=-10.0, u_max=10.0, anti_windup=True, h_override=None):
    """Simulate sampled controller and continuous plant; return JSON-friendly data.

    We deliberately use the same first-order plant, sample boundaries, and
    Euler h rule as Stage 1, so Ki=Kd=0 reproduces its P-only results.
    """
    K = _finite("K", K)
    tau = _finite("tau", tau)
    Kp = _finite("Kp", Kp)
    Ki = _finite("Ki", Ki)
    Kd = _finite("Kd", Kd)
    Ts = _finite("Ts", Ts)
    setpoint = _finite("setpoint", setpoint)
    duration = _finite("duration", duration)
    u_min = _finite("u_min", u_min)
    u_max = _finite("u_max", u_max)
    if not isinstance(anti_windup, bool):
        raise ValueError("anti_windup must be true or false.")
    if not 0.1 <= K <= 5:
        raise ValueError("K must be between 0.1 and 5.")
    if not 0.1 <= tau <= 5:
        raise ValueError("tau must be between 0.1 and 5 seconds.")
    if not 0 <= Kp <= 20:
        raise ValueError("Kp must be between 0 and 20.")
    if not 0 <= Ki <= 10:
        raise ValueError("Ki must be between 0 and 10.")
    if not 0 <= Kd <= 5:
        raise ValueError("Kd must be between 0 and 5.")
    if not 0.02 <= Ts <= 2:
        raise ValueError("Ts must be between 0.02 and 2 seconds.")
    if not 0.1 <= setpoint <= 5:
        raise ValueError("setpoint must be between 0.1 and 5.")
    if not 2 <= duration <= 12:
        raise ValueError("duration must be between 2 and 12 seconds.")
    if not (-100 <= u_min < u_max <= 100):
        raise ValueError("Command limits require -100 <= min < max <= 100.")
    if not (u_min <= 0 <= u_max):
        raise ValueError("Command limits must include 0.")

    if h_override is not None:
        h_override = _finite("h_override", h_override)
        if not 0 < h_override <= min(0.01, tau/10.0, Ts/10.0):
            raise ValueError("h_override must be a small positive Euler step.")
    h_target = (min(0.01, tau/100.0, Ts/20.0)
                if h_override is None else h_override)
    y = 0.0
    integral_state = 0.0  # integral of error multiplied by Ki
    previous_error = None
    time, output = [0.0], [0.0]
    control_time, control = [], []
    sample_error, raw_command = [], []
    p_terms, i_terms, d_terms = [], [], []
    integral_states = []
    saturation_flags, frozen_flags = [], []
    total_euler_steps = 0
    sample_count = math.ceil(duration/Ts - 1e-12)

    for k in range(sample_count):
        sample_time = k*Ts
        e = setpoint-y
        p_term = Kp*e
        # The homework formula uses a discrete derivative of error.
        # At k=0 use e[-1] = e[0] to avoid derivative kick at startup.
        d_term = 0.0 if previous_error is None else Kd*(e-previous_error)/Ts
        candidate_i = integral_state + Ki*Ts*e
        proposed_raw = p_term + candidate_i + d_term
        # Conditional anti-windup: do not integrate in the direction of
        # saturation. Still allow integration when error relieves it.
        freeze = bool(anti_windup and Ki > 0 and (
            (proposed_raw > u_max and e > 0) or
            (proposed_raw < u_min and e < 0)))
        if not freeze:
            integral_state = candidate_i
        i_term = integral_state
        u_raw = p_term+i_term+d_term
        u = min(u_max, max(u_min, u_raw))

        control_time.append(sample_time)
        control.append(u)
        sample_error.append(e)
        raw_command.append(u_raw)
        p_terms.append(p_term)
        i_terms.append(i_term)
        d_terms.append(d_term)
        integral_states.append(integral_state)
        saturation_flags.append(abs(u-u_raw) > 1e-10)
        frozen_flags.append(freeze)
        previous_error = e

        next_time = min(duration, (k+1)*Ts)
        interval = next_time-sample_time
        if interval <= 0:
            break
        n = max(1, math.ceil(interval/h_target))
        h = interval/n
        total_euler_steps += n
        for j in range(1, n+1):
            y += h*(K*u-y)/tau
            time.append(sample_time+j*h)
            output.append(y)

    # Final endpoint closes the last held command for Plotly step chart.
    control_time.append(duration)
    control.append(control[-1])
    raw_command.append(raw_command[-1])
    peak=max(output)
    t10 = _crossing_time(time, output, .1*setpoint)
    t90 = _crossing_time(time, output, .9*setpoint)
    settling_time=None
    staying=True
    for i in range(len(time)-1,-1,-1):
        staying=staying and abs(output[i]-setpoint) <= .02*setpoint
        if staying:
            settling_time=time[i]
    return {
        "parameters": {"K":K,"tau":tau,"Kp":Kp,"Ki":Ki,"Kd":Kd,
                       "Ts":Ts,"setpoint":setpoint,"duration":duration,
                       "u_min":u_min,"u_max":u_max,"anti_windup":anti_windup},
        "time": time,"output":output,
        "control_time":control_time,"control":control,
        "sample_error":sample_error,"raw_command":raw_command,
        "p_term":p_terms,"i_term":i_terms,"d_term":d_terms,
        "integral_state":integral_states,
        "saturated":saturation_flags,"integral_frozen":frozen_flags,
        "metrics":{
            "overshoot_percent":max(0.0,(peak-setpoint)/setpoint*100),
            "end_of_window_error_percent":(setpoint-output[-1])/setpoint*100,
            "rise_time_seconds":None if t10 is None or t90 is None else t90-t10,
            "settling_time_seconds":settling_time,
            "saturated_intervals":sum(saturation_flags),
            "frozen_integral_intervals":sum(frozen_flags),
            "sampling_intervals":len(sample_error),
            "euler_steps":total_euler_steps,
            "euler_target_step":h_target
        }
    }


def simulate_json(params_json):
    return json.dumps(simulate_pid(**json.loads(params_json)),allow_nan=False)


if __name__ == '__main__':
    for title,gains in [('P only',{'Kp':2,'Ki':0,'Kd':0}),
                         ('PI',{'Kp':2,'Ki':1,'Kd':0}),
                         ('PID',{'Kp':2,'Ki':1,'Kd':.2})]:
        d=simulate_pid(**gains,Ts=.05,duration=12)
        print(title, '| first u:',round(d['control'][0],4),
              '| output at 12s:',round(d['output'][-1],4),
              '| error (%):',round(d['metrics']['end_of_window_error_percent'],3))


# STAGE 3: Generate an Arduino sketch for the SAME sampled PID algorithm.
# Numerical calculations remain in simulate_pid; the generated sketch implements
# the matching controller-side equations, with replaceable hardware adapters.
def _cpp_float(value):
    """Portable finite Arduino float literal; parameters are prevalidated."""
    token = format(float(value), '.9g')
    if '.' not in token and 'e' not in token.lower():
        token += '.0'
    return token + 'f'


ARDUINO_TEMPLATE = r"""// P3 - Digital PID controller - (generated by the Python model)
// ENCS4380 / T19 - learning template; REVIEW HARDWARE ADAPTER BEFORE USE.
// Model: e = setpoint - measured output (in the same units).
// Initial conditions: integral = 0, first D = 0 (no derivative kick).
// PID update every Ts, output held between updates (sample-and-hold).
// Controller matches digital_pid.py; plant is simulated ONLY in the webpage.

#include <Arduino.h>
#include <math.h>

const float KP = @KP@;
const float KI = @KI@;
const float KD = @KD@;
const float SETPOINT = @SETPOINT@;
const float U_MIN = @U_MIN@;
const float U_MAX = @U_MAX@;
const bool ANTI_WINDUP = @ANTI_WINDUP@;
const unsigned long SAMPLE_INTERVAL_MS = @TS_MS@UL;
const float TS_SECONDS = @TS_SECONDS@;

// These are EXAMPLE pin assignments, NOT WALL-E's verified wiring.
const uint8_t SENSOR_PIN = A0;
const uint8_t MOTOR_PWM_PIN = 9;
const uint8_t MOTOR_DIR_A = 7;
const uint8_t MOTOR_DIR_B = 8;

float integralState = 0.0f;
float previousError = 0.0f;
bool hasPreviousError = false;
unsigned long previousSampleMs = 0;
float lastAppliedCommand = 0.0f;

float clampCommand(float value) {
  if (value < U_MIN) return U_MIN;
  if (value > U_MAX) return U_MAX;
  return value;
}

// HARDWARE ADAPTER #1 (EXAMPLE): A0 voltage maps to 0..5 model units.
// Replace with encoder speed readout in RPM or rad/s for WALL-E.
// Encoder units MUST match SETPOINT; calibrate before running a real motor.
float readPlantOutput() {
  const float SENSOR_FULL_SCALE = 5.0f;  // example only
  return (analogRead(SENSOR_PIN) / 1023.0f) * SENSOR_FULL_SCALE;
}

// HARDWARE ADAPTER #2 (EXAMPLE): bipolar H-bridge with two direction pins.
// The simulation's u range is MODEL UNITS, not calibrated motor PWM.
// Map command range into 0..255 PWM; replace to match the actual driver.
void applyActuator(float command) {
  if (fabsf(command) < 1e-7f) {
    analogWrite(MOTOR_PWM_PIN, 0);
    digitalWrite(MOTOR_DIR_A, LOW);
    digitalWrite(MOTOR_DIR_B, LOW);
    return;
  }
  const bool forward = command > 0.0f;
  const float span = forward ? U_MAX : -U_MIN;
  const float dutyFraction = (span > 0.0f) ? fabsf(command) / span : 0.0f;
  int duty = (int)(255.0f * dutyFraction + 0.5f);
  if (duty > 255) duty = 255;
  if (duty < 0) duty = 0;
  digitalWrite(MOTOR_DIR_A, forward ? HIGH : LOW);
  digitalWrite(MOTOR_DIR_B, forward ? LOW : HIGH);
  analogWrite(MOTOR_PWM_PIN, duty);
}

void updateController() {
  const float measuredOutput = readPlantOutput();
  const float error = SETPOINT - measuredOutput;
  const float pTerm = KP * error;
  const float dTerm = hasPreviousError
      ? KD * (error - previousError) / TS_SECONDS : 0.0f;

  const float candidateIntegral = integralState + KI * TS_SECONDS * error;
  const float proposedRaw = pTerm + candidateIntegral + dTerm;
  const bool pushingHigh = proposedRaw > U_MAX && error > 0.0f;
  const bool pushingLow = proposedRaw < U_MIN && error < 0.0f;
  const bool freezeIntegral = ANTI_WINDUP && KI > 0.0f
      && (pushingHigh || pushingLow);
  if (!freezeIntegral) {
    integralState = candidateIntegral;
  }

  const float rawCommand = pTerm + integralState + dTerm;
  lastAppliedCommand = clampCommand(rawCommand);
  applyActuator(lastAppliedCommand);
  previousError = error;
  hasPreviousError = true;
}

void setup() {
  pinMode(SENSOR_PIN, INPUT);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_DIR_A, OUTPUT);
  pinMode(MOTOR_DIR_B, OUTPUT);
  analogWrite(MOTOR_PWM_PIN, 0);
  digitalWrite(MOTOR_DIR_A, LOW);
  digitalWrite(MOTOR_DIR_B, LOW);
  previousSampleMs = millis();
  updateController();  // k=0 occurs immediately, like the Python simulation.
}

void loop() {
  const unsigned long nowMs = millis();
  if ((unsigned long)(nowMs - previousSampleMs) < SAMPLE_INTERVAL_MS) return;
  previousSampleMs += SAMPLE_INTERVAL_MS;
  // If the loop was late by a full period, skip missed ticks; do not run
  // several stale sensor updates back-to-back.
  if ((unsigned long)(nowMs - previousSampleMs) >= SAMPLE_INTERVAL_MS) {
    previousSampleMs = nowMs;
  }
  updateController();
}
"""


def generate_arduino_code(params_json):
    """Generate full Arduino .ino source for current page PID settings.

    Does not pretend to supply encoder/PWM calibration or WALL-E wiring.
    """
    incoming = json.loads(params_json)
    p = simulate_pid(**incoming)['parameters']  # validate using our model
    period_ms = int(p['Ts'] * 1000 + 0.5)
    if abs(period_ms / 1000.0 - p['Ts']) > 1e-7:
        raise ValueError('Arduino millis() needs a whole-millisecond Ts (e.g. 0.05 or 0.2 s).')
    replacements = {
        '@KP@': _cpp_float(p['Kp']),
        '@KI@': _cpp_float(p['Ki']),
        '@KD@': _cpp_float(p['Kd']),
        '@SETPOINT@': _cpp_float(p['setpoint']),
        '@U_MIN@': _cpp_float(p['u_min']),
        '@U_MAX@': _cpp_float(p['u_max']),
        '@ANTI_WINDUP@': 'true' if p['anti_windup'] else 'false',
        '@TS_MS@': str(period_ms),
        '@TS_SECONDS@': _cpp_float(p['Ts']),
    }
    result = ARDUINO_TEMPLATE
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


# Stage 5: fair comparison of two sampling times, all other values fixed.
# "similar" means a change within 0.5 percentage points of overshoot.
SIMILAR_TOLERANCE_PP = 0.5

def compare_sampling_times(baseline, new_Ts):
    if not isinstance(baseline, dict):
        raise ValueError("baseline must be a settings dictionary")
    base = simulate_pid(**baseline)["parameters"]  # validate settings
    new_Ts = _finite("new_Ts", new_Ts)
    if not 0.02 <= new_Ts <= 2 or new_Ts <= base["Ts"] + 1e-10:
        raise ValueError("Increase Ts above its saved value (up to 2 s).")
    # Identical target Euler step for both runs; numerical accuracy is not
    # confused with the sampling interval's effect on the controller.
    h = min(0.0025, base["tau"]/200, base["Ts"]/40)
    before = simulate_pid(**base, h_override=h)
    after = simulate_pid(**dict(base, Ts=new_Ts), h_override=h)
    delta = (after["metrics"]["overshoot_percent"]
             - before["metrics"]["overshoot_percent"])
    trend = "increase" if delta > SIMILAR_TOLERANCE_PP else (
        "decrease" if delta < -SIMILAR_TOLERANCE_PP else "similar")
    return {"baseline":before,"changed":after,"delta_pp":delta,
            "outcome":trend,"tolerance_pp":SIMILAR_TOLERANCE_PP,"common_h":h}

def compare_sampling_times_json(payload_json):
    payload=json.loads(payload_json)
    if not isinstance(payload,dict) or set(payload)!={"baseline","new_Ts"}:
        raise ValueError("Provide baseline and new_Ts only.")
    return json.dumps(compare_sampling_times(payload["baseline"],payload["new_Ts"]),allow_nan=False)


# Stage 5: compact validation checks for the digital PID page.
def run_validation_checks_json():
    """Reference checks from Homework 2 section 2.1, evaluated at startup.

    The analytical continuous-time checks and digital numerical approximations
    are displayed separately. For sampled control, exact transient matching
    cannot generally be expected for finite Ts.
    """
    K, tau, kp = 1.0, 1.0, 9.0
    tau_closed = tau / (1 + K * kp)
    steady_error_p = 100 / (1 + K * kp)
    p = simulate_pid(K=K, tau=tau, Kp=kp, Ki=0, Kd=0,
                     Ts=0.02, duration=5.0, setpoint=1.0)
    simulated_error_p = p["metrics"]["end_of_window_error_percent"]
    target = (K * kp / (1 + K * kp)) * (1-math.exp(-1))
    sampled_time_constant = _crossing_time(p["time"], p["output"], target)
    ok_p = (abs(tau_closed-0.1) <= 1e-9
            and abs(steady_error_p-10) <= 1e-9
            and sampled_time_constant is not None
            and abs(sampled_time_constant-0.1) <= 0.02
            and abs(simulated_error_p-10) <= 0.25)

    K, tau, kp, ki = 1.0, 1.0, 1.0, 1.0
    natural_frequency = math.sqrt(K*ki/tau)
    damping_ratio = (1+K*kp)/(2*math.sqrt(tau*K*ki))
    ok_pi = abs(natural_frequency-1) < 1e-9 and abs(damping_ratio-1) < 1e-9

    # At finite simulation duration, a stable PI loop approaches, but cannot
    # exactly reach, zero error. Avoid claiming a finite-time value is exact 0.
    pi = simulate_pid(K=K, tau=tau, Kp=kp, Ki=ki, Kd=0,
                      Ts=0.02, duration=12.0, setpoint=1.0)
    pi_error = abs(pi["metrics"]["end_of_window_error_percent"])
    ok_zero = pi_error <= 0.1

    checks = [
        {"pass":ok_p,
         "expected":"τcl = 0.100 s; steady-state error = 10.00%",
         "measured": (f"formula τcl = {tau_closed:.3f} s; "
                      f"sampled τ63 ≈ {sampled_time_constant:.3f} s; "
                      f"simulation error = {simulated_error_p:.3f}%"),
         "detail":"Tolerance: ±0.020 s for sampled τ63; ±0.25 percentage points for sampled error. Ts=0.02 s."},
        {"pass":ok_pi,
         "expected":"ωn = 1.000 rad/s; ζ = 1.000",
         "measured":f"ωn = {natural_frequency:.3f} rad/s; ζ = {damping_ratio:.3f}",
         "detail":"Computed from the continuous-time PI closed-loop coefficients as required by the homework."},
        {"pass":ok_zero,
         "expected":"Steady-state error = 0% for a stable step-tracking PI loop",
         "measured":f"Absolute end-window error = {pi_error:.4f}% at 12 s",
         "detail":"Numerical tolerance ≤ 0.1% at 12 s; K=1, τ=1 s, Kp=1, Ki=1, Ts=0.02 s."},
    ]
    return json.dumps({"checks":checks,"all_passed":all(c["pass"] for c in checks)},allow_nan=False)

