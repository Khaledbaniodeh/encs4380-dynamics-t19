"""Run locally with: python -m unittest discover -s tests -v"""
import math
import random
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from guess_sensor import (
    first_order_step, first_order_sine, second_order_step,
    new_sensor, reveal_guess, parameter_score, score_guess,
)


class SensorModelTests(unittest.TestCase):
    def test_first_order_632_and_95(self):
        for gain, tau in ((1.0, 2.0), (2.5, 0.7)):
            self.assertAlmostEqual(first_order_step(tau, gain, tau) / gain, 1 - math.exp(-1), places=12)
            self.assertAlmostEqual(first_order_step(3 * tau, gain, tau) / gain, 1 - math.exp(-3), places=12)

    def test_second_order_overshoot(self):
        zeta, wn = 0.5, 2.0
        peak_t = math.pi / (wn * math.sqrt(1 - zeta ** 2))
        actual_overshoot = second_order_step(peak_t, zeta, wn) - 1.0
        self.assertAlmostEqual(actual_overshoot, math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2)), places=10)

    def test_sine_transfer_amplitude_and_phase(self):
        k, tau, omega = 2.0, 1.5, 1.2
        amplitude = k / math.sqrt(1 + (omega * tau)**2)
        phase = -math.atan(omega * tau)
        for t in (0.0, 0.5, 1.0, 2.0, 5.0):
            self.assertAlmostEqual(first_order_sine(t, k, tau, omega), amplitude * math.sin(omega*t + phase), places=12)

    def test_random_sensors_all_modes(self):
        for sensor, response_kind in (("first_order", "step"), ("first_order", "sine"), ("second_order", "step")):
            ch = new_sensor(random.Random(42), sensor_type=sensor, response_kind=response_kind)
            self.assertEqual(ch["type"], sensor)
            self.assertEqual(ch["response_kind"], response_kind)
            self.assertEqual(len(ch["time"]), len(ch["clean_response"]))
            self.assertEqual(len(ch["time"]), len(ch["noisy_response"]))
            self.assertTrue(all(math.isfinite(v) for v in ch["noisy_response"]))
            if response_kind == "sine":
                self.assertGreater(ch["frequency"], 0)
                self.assertEqual(len(ch["input_signal"]), len(ch["time"]))
                self.assertGreater(ch["duration"] if "duration" in ch else ch["time"][-1], 0)
            else:
                self.assertIsNone(ch["input_signal"])
                self.assertAlmostEqual(ch["noisy_response"][0], 0)
            # A full-accuracy guess always recreates the noiseless response.
            revealed = reveal_guess(ch, ch["parameters"])
            for a, b in zip(revealed["clean_response"], revealed["predicted_response"]):
                self.assertAlmostEqual(a, b, places=10)
            self.assertEqual(score_guess(ch, ch["parameters"])["round_score"], 100)

    def test_random_challenges_estimable_from_window(self):
        for seed in range(100):
            ch = new_sensor(random.Random(seed))
            if ch["type"] == "first_order" and ch["response_kind"] == "step":
                self.assertGreaterEqual(ch["time"][-1], 5 * ch["parameters"]["tau"] - 1e-8)
            if ch["type"] == "second_order":
                z, wn = ch["parameters"]["zeta"], ch["parameters"]["omega_n"]
                peak_t = math.pi / (wn * math.sqrt(1-z*z))
                self.assertLess(peak_t, ch["time"][-1])
            if ch["response_kind"] == "sine":
                self.assertGreaterEqual(ch["time"][-1] * ch["frequency"] / (2 * math.pi), 3.99)

    def test_boundary_scores(self):
        for pct, expected in ((0, 100), (10, 100), (55, 50), (100, 0), (160, 0)):
            self.assertAlmostEqual(parameter_score(1 * (1 + pct/100), 1)["score"], expected, places=2)
        self.assertEqual(parameter_score(1e308, 1e-6)["score"], 0.0)
        self.assertTrue(math.isfinite(parameter_score(1e308, 1e-6)["error_percent"]))
        with self.assertRaises(ValueError):
            parameter_score(1, 0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            first_order_step(1, 1, 0)
        with self.assertRaises(ValueError):
            second_order_step(1, 1, 2)
        with self.assertRaises(ValueError):
            new_sensor(random.Random(42), sensor_type="second_order", response_kind="sine")
        with self.assertRaises(ValueError):
            first_order_sine(-1, 2, 1, 1)


if __name__ == "__main__":
    unittest.main()
