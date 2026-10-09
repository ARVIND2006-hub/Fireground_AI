#!/usr/bin/env python3
"""Run fixed/adaptive policy comparisons across multiple traffic-load scenarios."""
import argparse
import json
import statistics
from pathlib import Path

from traffic_digital_twin import simulate


SCENARIOS = {
    "balanced_light": (0.20, 0.20),
    "balanced_heavy": (0.55, 0.55),
    "ns_peak": (0.75, 0.20),
    "ew_peak": (0.20, 0.75),
    "near_saturation": (0.90, 0.85),
}


def run_benchmarks(steps: int, seeds: list[int]) -> dict:
    report = {
        "notice": "Toy queueing model only; not field-calibrated and not evidence of real-road improvement.",
        "steps_per_run": steps,
        "seeds": seeds,
        "scenarios": {},
    }
    for name, (ns_rate, ew_rate) in SCENARIOS.items():
        report["scenarios"][name] = {
            "arrival_ns": ns_rate,
            "arrival_ew": ew_rate,
            "policies": {},
        }
        for policy in ("fixed", "adaptive"):
            runs = [
                simulate(policy, steps, seed, ns_rate, ew_rate)
                for seed in seeds
            ]
            report["scenarios"][name]["policies"][policy] = {
                "runs": [r.__dict__ for r in runs],
                "mean_served": statistics.mean(r.served for r in runs),
                "mean_remaining": statistics.mean(r.remaining for r in runs),
                "mean_queue_delay_proxy": statistics.mean(r.mean_queue_delay_steps for r in runs),
                "mean_max_queue": statistics.mean(r.max_queue for r in runs),
                "mean_switch_count": statistics.mean(r.switch_count for r in runs),
            }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--seeds", type=int, nargs="+", default=[11, 22, 33, 44, 55])
    parser.add_argument("--output", type=Path, default=Path("traffic_benchmark_matrix.json"))
    args = parser.parse_args()
    if args.steps <= 0 or not args.seeds:
        parser.error("steps and seed list must be positive/non-empty")
    report = run_benchmarks(args.steps, args.seeds)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(SCENARIOS)} scenarios x 2 policies x {len(args.seeds)} seeds to {args.output}")


if __name__ == "__main__":
    main()
