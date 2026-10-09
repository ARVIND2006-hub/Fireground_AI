import unittest

from benchmark_scenarios import SCENARIOS, run_benchmarks


class BenchmarkScenarioTests(unittest.TestCase):
    def test_all_scenarios_have_both_policies(self):
        report = run_benchmarks(120, [11, 22])
        self.assertEqual(set(report["scenarios"]), set(SCENARIOS))
        for scenario in report["scenarios"].values():
            self.assertEqual(set(scenario["policies"]), {"fixed", "adaptive"})
            for policy in scenario["policies"].values():
                self.assertEqual(len(policy["runs"]), 2)
                self.assertGreaterEqual(policy["mean_served"], 0)
                self.assertGreaterEqual(policy["mean_remaining"], 0)

    def test_seeded_runs_are_repeatable(self):
        first = run_benchmarks(100, [123])
        second = run_benchmarks(100, [123])
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
