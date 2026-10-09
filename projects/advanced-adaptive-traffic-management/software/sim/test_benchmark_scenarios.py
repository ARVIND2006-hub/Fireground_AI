import unittest
from benchmark_scenarios import SCENARIOS, run_benchmarks


class BenchmarkScenarioTests(unittest.TestCase):
    def test_scenario_matrix_shape(self):
        report = run_benchmarks(50, [1, 2])
        self.assertEqual(set(report["scenarios"]), set(SCENARIOS))
        for scenario in report["scenarios"].values():
            self.assertEqual(set(scenario["policies"]), {"fixed", "adaptive"})
            for policy in scenario["policies"].values():
                self.assertEqual(len(policy["runs"]), 2)
                self.assertGreaterEqual(policy["mean_remaining"], 0)

    def test_repeatability(self):
        self.assertEqual(run_benchmarks(50, [7]), run_benchmarks(50, [7]))


if __name__ == "__main__":
    unittest.main()
