# Reproducible Benchmark Protocol

Run from the repository root:

```bash
python3 projects/advanced-adaptive-traffic-management/software/sim/benchmark_scenarios.py --steps 3000 --seeds 11 22 33 44 55 --output traffic_benchmark_matrix.json
python3 -m unittest discover -s projects/advanced-adaptive-traffic-management/software/sim -p "test_*.py"
```

The runner evaluates balanced light, balanced heavy, north-south peak, east-west peak, and near-saturation arrival probabilities. Each scenario runs both fixed and adaptive policies with identical seed lists. The JSON output includes individual runs and means for served vehicles, remaining queue, queue-delay proxy, maximum queue, and signal switches.

## Reporting rules
- Preserve the generated JSON with the exact source commit and command-line parameters.
- Do not cherry-pick only favorable scenarios; report the full matrix.
- Compare multiple seeds and disclose model assumptions.
- Do not call the queue-delay proxy measured per-vehicle travel time.
- Do not claim a real-world benefit from this toy model without calibration, a validated traffic simulator, and field data.
