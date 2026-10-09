#!/usr/bin/env python3
"""Small deterministic queueing digital twin for comparing signal policies.

This is a software experiment, not a calibrated traffic model. One simulation
step represents one abstract second; arrivals are seeded Bernoulli events and
each green lane serves at most one queued vehicle per step.
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Metrics:
    policy: str
    steps: int
    arrivals: int
    served: int
    remaining: int
    mean_queue_delay_steps: float
    max_queue: int
    switch_count: int


def simulate(policy: str, steps: int, seed: int,
             arrival_ns: float, arrival_ew: float,
             fixed_green: int = 20, min_green: int = 5,
             max_green: int = 35) -> Metrics:
    rng = random.Random(seed)
    queues = [0, 0]
    total_wait = 0
    arrivals = 0
    served = 0
    max_queue = 0
    switches = 0
    active = 0
    green_age = 0
    clearance = 0
    clearance_remaining = 0

    for _ in range(steps):
        for lane, rate in enumerate((arrival_ns, arrival_ew)):
            if rng.random() < rate:
                queues[lane] += 1
                arrivals += 1

        total_wait += queues[0] + queues[1]
        max_queue = max(max_queue, queues[0], queues[1])

        if clearance_remaining > 0:
            clearance_remaining -= 1
            if clearance_remaining == 0:
                active = 1 - active
                green_age = 0
            continue

        if queues[active] > 0:
            queues[active] -= 1
            served += 1
        green_age += 1

        if policy == "fixed":
            should_switch = green_age >= fixed_green
        elif policy == "adaptive":
            other = 1 - active
            should_switch = (
                green_age >= max_green
                or (green_age >= min_green and queues[other] > queues[active])
                or (green_age >= min_green and queues[active] == 0 and queues[other] > 0)
            )
        else:
            raise ValueError(f"unknown policy: {policy}")

        if should_switch:
            switches += 1
            clearance_remaining = clearance
            if clearance_remaining == 0:
                active = 1 - active
                green_age = 0

    return Metrics(
        policy=policy,
        steps=steps,
        arrivals=arrivals,
        served=served,
        remaining=sum(queues),
        mean_queue_delay_steps=(total_wait / arrivals) if arrivals else 0.0,
        max_queue=max_queue,
        switch_count=switches,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--arrival-ns", type=float, default=0.65)
    parser.add_argument("--arrival-ew", type=float, default=0.25)
    parser.add_argument("--output", type=Path, default=Path("traffic_digital_twin_report.json"))
    args = parser.parse_args()
    if args.steps <= 0 or not (0 <= args.arrival_ns <= 1) or not (0 <= args.arrival_ew <= 1):
        parser.error("steps must be positive and arrival rates must be in [0, 1]")

    fixed = simulate("fixed", args.steps, args.seed, args.arrival_ns, args.arrival_ew)
    adaptive = simulate("adaptive", args.steps, args.seed, args.arrival_ns, args.arrival_ew)
    report = {
        "model_notice": "Toy queueing model; results are not field-calibrated or a claim of real-road improvement.",
        "scenario": {
            "steps": args.steps,
            "seed": args.seed,
            "arrival_probability_ns_per_step": args.arrival_ns,
            "arrival_probability_ew_per_step": args.arrival_ew,
        },
        "results": [asdict(fixed), asdict(adaptive)],
        "adaptive_minus_fixed_mean_delay": adaptive.mean_queue_delay_steps - fixed.mean_queue_delay_steps,
        "adaptive_minus_fixed_served": adaptive.served - fixed.served,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
