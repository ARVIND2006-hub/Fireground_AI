# TEMPLATE ONLY — replace every placeholder for the exact FPGA board.
# Do not use this file unchanged for implementation.
# Example 100 MHz clock: 10.000 ns period. Change to match the board clock.
create_clock -name sys_clk -period 10.000 [get_ports {aclk}]

# Add board-specific input/output delays after selecting the correct interface
# and external device timing. Do not guess these values.
# set_input_delay  -clock sys_clk <ns> [get_ports {sensor_input}]
# set_output_delay -clock sys_clk <ns> [get_ports {signal_output}]

# Add pin constraints using the exact FPGA part and board schematic:
# set_property PACKAGE_PIN <PIN> [get_ports {aclk}]
# set_property IOSTANDARD <IOSTANDARD> [get_ports {aclk}]

# Review asynchronous input synchronizers and tool-specific CDC constraints.
# Do not apply blanket false paths without a documented CDC analysis.
