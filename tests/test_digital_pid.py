"""Homework 2 P3 — regression checks for the published Digital PID model."""
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
import digital_pid as m


class DigitalPIDTests(unittest.TestCase):
    def test_homework_validation_is_complete_and_passes(self):
        result = json.loads(m.run_validation_checks_json())
        self.assertEqual(len(result["checks"]), 3)
        self.assertTrue(result["all_passed"])
        self.assertTrue(all(row["pass"] for row in result["checks"]))

    def test_p_only_steady_state_reference(self):
        r = m.simulate_pid(K=1, tau=1, Kp=9, Ki=0, Kd=0, Ts=0.02, duration=5)
        self.assertAlmostEqual(r["metrics"]["end_of_window_error_percent"], 10, delta=0.25)

    def test_pi_removes_step_error(self):
        r = m.simulate_pid(K=1, tau=1, Kp=1, Ki=1, Kd=0, Ts=0.02, duration=12)
        self.assertLess(abs(r["metrics"]["end_of_window_error_percent"]), 0.1)

    def test_p_only_has_zero_integral_and_derivative(self):
        r = m.simulate_pid(Kp=2, Ki=0, Kd=0, Ts=0.1)
        self.assertTrue(all(abs(x) < 1e-12 for x in r["i_term"]))
        self.assertTrue(all(abs(x) < 1e-12 for x in r["d_term"]))

    def test_first_sample_derivative_zero(self):
        r = m.simulate_pid(Kp=2, Ki=1, Kd=0.3, Ts=0.1)
        self.assertAlmostEqual(r["d_term"][0], 0.0)

    def test_first_integral_includes_first_sample(self):
        r = m.simulate_pid(Kp=0, Ki=1, Kd=0, Ts=0.1, setpoint=1)
        self.assertAlmostEqual(r["i_term"][0], 0.1, delta=1e-10)

    def test_first_control_interval_is_held(self):
        r = m.simulate_pid(K=1, tau=1, Kp=2, Ki=0, Kd=0, Ts=0.2)
        self.assertAlmostEqual(r["control"][0], 2.0)
        self.assertAlmostEqual(r["control_time"][1], 0.2)
        self.assertGreater(r["output"][-1], 0)

    def test_command_stays_inside_limits(self):
        r = m.simulate_pid(Kp=20, Ki=5, Ts=0.05, u_min=-0.5, u_max=0.5)
        self.assertLessEqual(max(r["control"]), 0.5 + 1e-9)
        self.assertGreaterEqual(min(r["control"]), -0.5 - 1e-9)

    def test_antiwindup_blocks_integral_accumulation(self):
        params = dict(Kp=2, Ki=6, Kd=0, Ts=0.2, duration=10, u_min=-10, u_max=2)
        enabled = m.simulate_pid(**params, anti_windup=True)
        disabled = m.simulate_pid(**params, anti_windup=False)
        self.assertGreater(enabled["metrics"]["frozen_integral_intervals"], 0)
        self.assertEqual(disabled["metrics"]["frozen_integral_intervals"], 0)

    def test_sampling_time_affects_overshoot(self):
        params = dict(K=1, tau=1, Kp=9, Ki=0, Kd=0, Ts=0.05, duration=5)
        before = m.simulate_pid(**params)
        after = m.simulate_pid(**dict(params, Ts=0.20))
        self.assertGreater(after["metrics"]["overshoot_percent"],
                           before["metrics"]["overshoot_percent"] + 20)

    def test_prediction_comparison_uses_equal_euler_step(self):
        baseline = dict(K=1, tau=1, Kp=9, Ki=0, Kd=0, Ts=0.05,
                        setpoint=1, duration=5, u_min=-10, u_max=10,
                        anti_windup=True)
        r = m.compare_sampling_times(baseline, 0.2)
        self.assertEqual(r["outcome"], "increase")
        self.assertAlmostEqual(r["baseline"]["metrics"]["euler_target_step"],
                               r["changed"]["metrics"]["euler_target_step"])

    def test_prediction_rejects_nonincreasing_sampling(self):
        with self.assertRaises(ValueError):
            m.compare_sampling_times({"Ts": 0.2}, 0.2)

    def test_arduino_matches_current_settings(self):
        c = m.generate_arduino_code(json.dumps(
            dict(Kp=3, Ki=1.25, Kd=0.15, Ts=0.08, anti_windup=False)))
        for expected in ("const float KP = 3.0f", "const float KI = 1.25f",
                         "const float KD = 0.15f", "ANTI_WINDUP = false",
                         "SAMPLE_INTERVAL_MS = 80UL"):
            self.assertIn(expected, c)

    def test_arduino_rejects_fractional_milliseconds(self):
        with self.assertRaises(ValueError):
            m.generate_arduino_code(json.dumps({"Ts": 0.0205}))

    def test_validations_are_independent_of_sliders(self):
        first = m.run_validation_checks_json()
        m.simulate_pid(Kp=17, Ki=2, Kd=0.5, Ts=0.4)
        self.assertEqual(first, m.run_validation_checks_json())

    def test_invalid_inputs_are_rejected(self):
        for params in (dict(tau=0), dict(Ts=0), dict(Kp=-1),
                       dict(u_min=1, u_max=10)):
            with self.subTest(params=params):
                with self.assertRaises(ValueError):
                    m.simulate_pid(**params)


if __name__ == "__main__":
    unittest.main()
