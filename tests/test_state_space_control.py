
"""Regression tests for Homework 2 State-Space Pole Placement bonus."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from state_space_control import (
    dashboard_json,
    eigenvalues,
    pole_placement,
    rk4_simulation,
    validate_parameters,
)

import json


class TestStateSpaceControl(unittest.TestCase):

    def test_module3_original_poles(self):
        design = pole_placement(1, 2, 4, 0.7, 3)
        poles = design["open_poles"]
        self.assertAlmostEqual(poles[0].real, -1)
        self.assertAlmostEqual(abs(poles[0].imag), math.sqrt(3))

    def test_feedback_gains(self):
        design = pole_placement(1, 2, 4, 0.7, 3)
        self.assertAlmostEqual(design["K1"], 5)
        self.assertAlmostEqual(design["K2"], 2.2)

    def test_closed_loop_poles(self):
        design = pole_placement(1, 2, 4, 0.7, 3)
        poles = design["closed_poles"]
        self.assertAlmostEqual(poles[0].real, -2.1)
        self.assertAlmostEqual(abs(poles[0].imag), 3 * math.sqrt(1 - 0.7**2))

    def test_critical_damping(self):
        design = pole_placement(1, 2, 4, 1, 3)
        for pole in design["closed_poles"]:
            self.assertAlmostEqual(pole.real, -3)
            self.assertAlmostEqual(pole.imag, 0)

    def test_overdamped_poles(self):
        design = pole_placement(1, 2, 4, 1.5, 3)
        poles = design["closed_poles"]
        self.assertTrue(all(abs(p.imag) < 1e-9 for p in poles))
        self.assertTrue(all(p.real < 0 for p in poles))

    def test_original_system_unchanged(self):
        design = pole_placement(1, 2, 4, 0.7, 3)
        self.assertEqual(design["A"], [[0, 1], [-4, -2]])
        self.assertEqual(design["B"], [[0], [1]])

    def test_zero_feedback_matches_open_loop(self):
        design = pole_placement(1, 2, 4, 0.5, 2)
        self.assertAlmostEqual(design["K1"], 0)
        self.assertAlmostEqual(design["K2"], 0)

    def test_rk4_initial_conditions(self):
        response = rk4_simulation(1, 2, 4, 5, 2.2, 1, 0, 12)
        self.assertEqual(response["position"][0], 1)
        self.assertEqual(response["velocity"][0], 0)
        self.assertAlmostEqual(response["control"][0], -5)

    def test_closed_loop_converges(self):
        response = rk4_simulation(1, 2, 4, 5, 2.2, 1, 0, 12)
        self.assertLess(abs(response["position"][-1]), 1e-7)
        self.assertLess(abs(response["velocity"][-1]), 1e-7)

    def test_open_loop_converges(self):
        response = rk4_simulation(1, 2, 4, 0, 0, 1, 0, 12)
        self.assertLess(abs(response["position"][-1]), 1e-4)

    def test_dashboard_output(self):
        result = json.loads(dashboard_json())
        self.assertEqual(len(result["open_response"]["time"]), 2001)
        self.assertEqual(len(result["closed_response"]["time"]), 2001)
        self.assertEqual(result["method"], "RK4")

    def test_invalid_mass(self):
        with self.assertRaises(ValueError):
            validate_parameters(0, 2, 4, 0.7, 3, 1, 0, 12)

    def test_invalid_damping(self):
        with self.assertRaises(ValueError):
            validate_parameters(1, 2, 4, -0.5, 3, 1, 0, 12)

    def test_invalid_frequency(self):
        with self.assertRaises(ValueError):
            validate_parameters(1, 2, 4, 0.7, 0, 1, 0, 12)

    def test_nonfinite_input(self):
        with self.assertRaises(ValueError):
            validate_parameters(1, 2, 4, math.nan, 3, 1, 0, 12)


if __name__ == "__main__":
    unittest.main()
