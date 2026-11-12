"""Regression tests for the two-sine superposition experiment (Module 2 v2)."""

import importlib.util
import json
import math
from pathlib import Path
import unittest


MODEL = Path(__file__).resolve().parents[1] / "python" / "First-order frequency response.py"
spec = importlib.util.spec_from_file_location("first_order_frequency", MODEL)
frequency = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frequency)


class SuperpositionTests(unittest.TestCase):
    def get_result(self, tau=0.2, omega1=2.0, omega2=12.0, amplitude2=0.6):
        return json.loads(frequency.superposition_json(tau, omega1, omega2, amplitude2))

    def test_default_component_ratios_and_phase(self):
        data = self.get_result()
        self.assertAlmostEqual(data["m1"], 1 / math.sqrt(1 + 0.4 ** 2), places=12)
        self.assertAlmostEqual(data["m2"], 1 / math.sqrt(1 + 2.4 ** 2), places=12)
        self.assertAlmostEqual(data["m2"], 1 / 2.6, places=12)
        self.assertLess(data["m2"], data["m1"])
        self.assertLess(data["phase2_degrees"], data["phase1_degrees"])

    def test_waveform_is_sum_of_two_filtered_components(self):
        data = self.get_result()
        self.assertEqual(len(data["time"]), len(data["input"]))
        self.assertEqual(len(data["time"]), len(data["output"]))
        for index in [0, 1, len(data["time"]) // 3, len(data["time"]) - 1]:
            t = data["time"][index]
            expected_input = math.sin(2 * t) + 0.6 * math.sin(12 * t)
            expected_output = (
                data["m1"] * math.sin(2 * t + math.radians(data["phase1_degrees"]))
                + 0.6 * data["m2"] * math.sin(12 * t + math.radians(data["phase2_degrees"]))
            )
            self.assertAlmostEqual(data["input"][index], expected_input, places=12)
            self.assertAlmostEqual(data["output"][index], expected_output, places=12)

    def test_zero_second_amplitude_is_one_sine(self):
        data = self.get_result(amplitude2=0)
        self.assertEqual(data["component2_output_amplitude"], 0)
        for t, x, y in zip(data["time"], data["input"], data["output"]):
            self.assertAlmostEqual(x, math.sin(2 * t), places=12)
            self.assertAlmostEqual(
                y, data["m1"] * math.sin(2 * t + math.radians(data["phase1_degrees"])),
                places=12
            )

    def test_equal_frequencies_combine_correctly(self):
        data = self.get_result(omega1=4.0, omega2=4.0, amplitude2=0.5)
        self.assertAlmostEqual(data["m1"], data["m2"], places=12)
        for t, x in zip(data["time"], data["input"]):
            self.assertAlmostEqual(x, 1.5 * math.sin(4 * t), places=12)

    def test_positive_tau_attenuates_faster_component(self):
        fast_sensor = self.get_result(tau=0.05)
        slow_sensor = self.get_result(tau=0.8)
        self.assertGreater(fast_sensor["m1"], slow_sensor["m1"])
        self.assertGreater(fast_sensor["m2"], slow_sensor["m2"])

    def test_bounded_sampling_and_finite_results(self):
        data = self.get_result(omega1=0.5, omega2=24, amplitude2=2)
        self.assertGreaterEqual(len(data["time"]), 421)
        self.assertLessEqual(len(data["time"]), 2501)
        self.assertTrue(all(map(math.isfinite, data["input"] + data["output"])))

    def test_reject_invalid_parameters(self):
        for args in [(0, 2, 12, 0.6), (0.2, 0.1, 12, 0.6),
                     (0.2, 2, 25, 0.6), (0.2, 2, 12, -0.1),
                     (0.2, 2, 12, 2.1), (math.inf, 2, 12, 0.6)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    frequency.superposition_json(*args)

if __name__ == "__main__":
    unittest.main()
