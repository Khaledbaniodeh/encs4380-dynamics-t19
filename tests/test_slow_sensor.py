import importlib.util
import json
import math
from pathlib import Path
import unittest

path = Path(__file__).parents[1] / "python/slow_sensor.py"
spec = importlib.util.spec_from_file_location("slow_sensor", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SlowSensorChecks(unittest.TestCase):
    def test_p_only_matches_independent_closed_form(self):
        data=m.simulate({"kp":9,"ki":0,"sensor_tau":0,"duration":5},False)["response"]
        errors=[abs(y-0.9*(1-math.exp(-10*t))) for t,y in zip(data["time"],data["true"])]
        self.assertLess(max(errors),1e-6)
        self.assertEqual(data["true"],data["measured"])

    def test_pi_baseline_matches_cancelled_transfer_function(self):
        data=m.simulate({"kp":1,"ki":1,"sensor_tau":0,"duration":20},False)["response"]
        self.assertLess(max(abs(y-(1-math.exp(-t))) for t,y in zip(data["time"],data["true"])),1e-7)
        self.assertLess(abs(1-data["true"][-1]),1e-7)

    def test_rk4_convergence(self):
        p=m.settings({"kp":9,"ki":0,"sensor_tau":0,"duration":5})
        a=m.integrate(p,4);b=m.integrate(p,2)
        error=lambda d:max(abs(y-0.9*(1-math.exp(-10*t))) for t,y in zip(d["time"],d["true"]))
        self.assertLess(error(b),error(a)/10)

    def test_slow_sensor_demonstrates_oscillation(self):
        fast=m.simulate({"sensor_tau":0.05},False)
        marginal=m.simulate({"sensor_tau":3},False)
        growing=m.simulate({"sensor_tau":4},False)
        self.assertGreater(marginal["metrics"]["overshoot"],fast["metrics"]["overshoot"]+20)
        self.assertIn("oscillation",marginal["metrics"]["motion"])
        self.assertIn("oscillation",growing["metrics"]["motion"])
        self.assertGreater(growing["metrics"]["overshoot"],marginal["metrics"]["overshoot"])
        self.assertGreater(growing["metrics"]["sensor_gap"],fast["metrics"]["sensor_gap"])

    def test_zero_and_signed_setpoints(self):
        zero=m.simulate({"setpoint":0},False)
        self.assertTrue(all(v==0 for v in zero["response"]["true"]))
        self.assertIsNone(zero["metrics"]["overshoot"])
        pos=m.simulate({"duration":5},False);neg=m.simulate({"setpoint":-1,"duration":5},False)
        self.assertLess(max(abs(a+b) for a,b in zip(pos["response"]["true"],neg["response"]["true"])),1e-10)

    def test_derivative_and_json_are_finite(self):
        result=m.simulate({"kd":0.3,"sensor_tau":0.1,"duration":10})
        for key in ("time","true","measured","control"):
            self.assertTrue(all(math.isfinite(v) for v in result["response"][key]))
        json.loads(m.simulate_json('{"sensor_tau":0.1,"duration":5}'))

    def test_sensor_initial_response_and_homework_checks(self):
        d=m.simulate({"duration":5},False)["response"]
        self.assertEqual(d["true"][0],0);self.assertEqual(d["measured"][0],0)
        self.assertGreater(d["true"][1],d["measured"][1])
        self.assertTrue(all(row["passed"] for row in json.loads(m.validation_json())))

    def test_invalid_inputs(self):
        for values in ({"sensor_tau":-1},{"sensor_tau":0.001},{"tau":0},{"kp":float('nan')},{"duration":1000}):
            with self.assertRaises(ValueError):m.simulate(values)

    def test_coupled_plant_and_sensor_match_independent_closed_form(self):
        d=m.simulate({"kp":1,"ki":0,"kd":0,"sensor_tau":1,"duration":10},False)["response"]
        for t,y,ym in zip(d["time"],d["true"],d["measured"]):
            decay=math.exp(-t)
            self.assertAlmostEqual(y,0.5*(1-decay*math.cos(t)+decay*math.sin(t)),places=7)
            self.assertAlmostEqual(ym,0.5*(1-decay*(math.cos(t)+math.sin(t))),places=7)

    def test_saturation_and_unreachable_setpoint(self):
        r=m.simulate({"u_min":-0.5,"u_max":0.5},False)
        self.assertTrue(r["response"]["saturated"])
        self.assertTrue(all(-0.5<=u<=0.5 for u in r["response"]["control"]))
        self.assertGreater(r["metrics"]["last_error"],0.49)

    def test_anti_windup_freezes_outward_and_allows_unwinding(self):
        p=m.settings({"u_min":-0.5,"u_max":0.5,"kd":0})
        self.assertEqual(m.signals([0,0,10],p)[2][2],0)
        self.assertLess(m.signals([2,2,10],p)[2][2],0)

    def test_ideal_derivative_with_saturation_is_consistent(self):
        p=m.settings({"sensor_tau":0,"kd":0.3,"u_min":-0.5,"u_max":0.5})
        ym,u,rates,saturated=m.signals([0.2,0.2,10],p)
        self.assertEqual(ym,0.2)
        self.assertEqual(u,0.5)
        self.assertTrue(saturated)
        self.assertAlmostEqual(rates[0],(p["K"]*u-0.2)/p["tau"])
        self.assertEqual(rates[0],rates[1])

    def test_invalid_control_limits(self):
        for values in ({"u_min":1},{"u_max":-1},{"u_min":0,"u_max":0},{"u_min":-101},{"u_max":101}):
            with self.assertRaises(ValueError):m.simulate(values)


if __name__ == '__main__':unittest.main()
