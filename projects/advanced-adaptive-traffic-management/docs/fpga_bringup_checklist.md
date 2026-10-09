# FPGA Bring-up Checklist

This checklist is for a low-voltage tabletop demonstration only. The project is not safety-certified and must never control public-road signals.

## Before synthesis
- [ ] Select the exact FPGA board, device part number, and tool version.
- [ ] Confirm top-level module and all source files.
- [ ] Run HDL compile and all simulation tests; preserve logs and waveforms.
- [ ] Resolve all errors and review every warning.
- [ ] Review reset polarity, reset release, clock-domain crossings, and asynchronous pulse widths.
- [ ] Decide whether standalone sensor/watchdog modules will be integrated; they are not wired into the current SoC top.

## Before implementation
- [ ] Replace the template clock period with the board's actual clock.
- [ ] Add correct pin assignments and I/O standards from the board schematic.
- [ ] Define external input/output delays where applicable.
- [ ] Run synthesis and inspect inferred latches, resource usage, and warnings.
- [ ] Run place-and-route and confirm positive timing slack for the specified constraints.
- [ ] Review CDC and reset-domain reports.

## Bench demonstration
- [ ] Start with LEDs or logic analyzer probes, not external traffic lamps.
- [ ] Use current-limited low-voltage outputs and proper driver circuitry.
- [ ] Verify startup all-red, mutually exclusive green, yellow interlock, pedestrian interlock, and fault behavior.
- [ ] Inject stuck, bouncing, missing, and repeated inputs.
- [ ] Record board revision, bitstream hash, clock frequency, test procedure, and observed results.
- [ ] Keep an independent emergency power-off method available.

## Release evidence
A credible portfolio release should include source revision, tool versions, test logs, synthesis reports, timing reports, and a short demo video. Never claim timing closure or hardware validation without the corresponding evidence.
