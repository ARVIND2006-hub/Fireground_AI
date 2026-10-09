# Digital-Twin Metrics

The Python queueing experiment compares a fixed-time signal policy with a queue-aware adaptive policy using the same pseudo-random seed and arrival parameters.

## Metrics emitted
- **Arrivals:** generated vehicles over the simulated horizon.
- **Served:** vehicles removed from queues during a green phase.
- **Remaining:** total queued vehicles at the end of the run.
- **Mean queue delay (approximation):** cumulative queue occupancy sampled each step divided by total arrivals. This is a coarse system-level proxy, not a per-vehicle measured travel delay.
- **Maximum queue:** largest observed queue length in either approach.
- **Switch count:** number of phase changes initiated.

## Experimental method
1. Fix the random seed and duration.
2. Use identical arrival rates for both policies.
3. Repeat across multiple seeds and balanced/unbalanced demand.
4. Compare mean and spread across repetitions, not just one run.
5. Include transition/clearance overhead and report all parameters.
6. Treat results as model outputs; do not extrapolate to real streets without calibration and field validation.

## Current limitation
This toy model uses independent Bernoulli arrivals and a simple one-vehicle-per-step service model. It does not model turning movements, pedestrians, platoons, lanes, road geometry, detector errors, spillback, weather, transit priority, or real-world traffic rules. No measured performance claim is made.
