"""Numerical regression checks for the optional Module 1 Euler comparison."""

import json
import math
import unittest

from python.first_order import euler_comparison, euler_comparison_json, forward_euler


class EulerTests(unittest.TestCase):
    def test_hand_calculated_step_updates(self):
        result = euler_comparison("step", 1, 2, 10, 0.5)
        self.assertEqual(result["times"][:3], [0.0, 0.5, 1.0])
        self.assertEqual(result["values"][:3], [0.0, 2.5, 4.375])
        self.assertAlmostEqual(result["max_abs_error"], 0.5147319117144233)
        self.assertEqual(result["steps"], 20)

    def test_ramp_uses_input_at_start_of_step(self):
        result = euler_comparison("ramp", 1, 2, 2, 0.5)
        self.assertEqual(result["values"][:3], [0.0, 0.0, 0.25])

    def test_reducing_step_reduces_error_for_both_inputs(self):
        for mode in ("step", "ramp"):
            with self.subTest(mode=mode):
                coarse = euler_comparison(mode, 1, 2, 10, 0.5)
                fine = euler_comparison(mode, 1, 2, 10, 0.1)
                self.assertLess(fine["max_abs_error"], coarse["max_abs_error"])
                self.assertLess(fine["final_abs_error"], coarse["final_abs_error"])

    def test_signed_and_zero_inputs(self):
        for mode in ("step", "ramp"):
            positive = euler_comparison(mode, 2, 2, 3, 0.5)
            negative = euler_comparison(mode, -2, 2, 3, 0.5)
            self.assertEqual(negative["values"], [-value for value in positive["values"]])
            self.assertEqual(negative["max_abs_error"], positive["max_abs_error"])
            for k, level in ((0, 3), (2, 0)):
                self.assertEqual(euler_comparison(mode, k, 2, level, 0.5)["max_abs_error"], 0)

    def test_final_partial_step_ends_at_requested_time(self):
        times, values = forward_euler(lambda t, y: 1.0, 0.0, 1.0, 0.3)
        self.assertEqual(times[-1], 1.0)
        self.assertAlmostEqual(values[-1], 1.0)
        self.assertEqual(len(times), 5)
        self.assertEqual(forward_euler(lambda t, y: 1, 2, 0, 0.1), ([0.0], [2.0]))

    def test_stability_boundary_and_numerical_instability(self):
        self.assertEqual(euler_comparison("step", 1, 2, 10, 4)["stability"], "boundary")
        unstable = euler_comparison("step", 1, 2, 10, 5)
        self.assertEqual(unstable["stability"], "unstable")
        self.assertEqual(unstable["values"], [0.0, 25.0, -12.5])

    def test_invalid_comparison_is_a_concise_json_error(self):
        invalid = [
            ("step", 1, 2, 10, 0), ("step", 1, 2, 10, -1),
            ("step", 1, 2, 10, 1e-9), ("step", 1, 0, 10, 0.5),
            ("bad", 1, 2, 10, 0.5), ("step", 1, 2, 10, math.nan),
        ]
        for args in invalid:
            with self.subTest(args=args):
                result = json.loads(euler_comparison_json(*args))
                self.assertFalse(result["ok"])
                self.assertTrue(result["message"])

    def test_nonfinite_derivative_is_rejected(self):
        with self.assertRaises(ValueError):
            forward_euler(lambda t, y: math.inf, 0, 1, 0.5)


if __name__ == "__main__":
    unittest.main()
