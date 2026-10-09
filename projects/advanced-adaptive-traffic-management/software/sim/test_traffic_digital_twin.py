import unittest
from traffic_digital_twin import simulate


class TrafficDigitalTwinTests(unittest.TestCase):
    def test_repeatable_seed(self):
        a = simulate("adaptive", 300, 7, 0.6, 0.2)
        b = simulate("adaptive", 300, 7, 0.6, 0.2)
        self.assertEqual(a, b)

    def test_accounting_and_bounds(self):
        result = simulate("fixed", 400, 9, 0.4, 0.3)
        self.assertGreaterEqual(result.arrivals, result.served)
        self.assertGreaterEqual(result.remaining, 0)
        self.assertGreaterEqual(result.max_queue, 0)
        self.assertLessEqual(result.served, result.arrivals)

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            simulate("magic", 20, 1, 0.2, 0.2)


if __name__ == "__main__":
    unittest.main()
