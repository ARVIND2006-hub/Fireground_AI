`timescale 1ns/1ps
module tb_advanced_traffic_management_controller;
    logic clk=0, rst_n=0;
    logic [3:0] ns_demand=0, ew_demand=0;
    logic sensor_data_valid=1;
    logic ns_emergency_async=0, ew_emergency_async=0;
    logic ped_ns_async=0, ped_ew_async=0;
    logic [1:0] ns_light, ew_light;
    logic ped_walk_ns, ped_walk_ew, emergency_active, fault_active;
    logic [3:0] debug_state;
    logic [7:0] debug_timer;
    integer i;

    localparam logic [1:0] RED=2'b00, YELLOW=2'b01, GREEN=2'b10;

    advanced_traffic_management_controller dut (.*);

    always #5 clk=~clk;

    // Simulation monitors for core output invariants.
    always @(negedge clk) if (rst_n) begin
        if (ns_light==GREEN && ew_light==GREEN)
            $fatal(1,"SAFETY FAILURE: both approaches green");
        if ((ped_walk_ns || ped_walk_ew) &&
            (ns_light!=RED || ew_light!=RED))
            $fatal(1,"SAFETY FAILURE: pedestrian walk without both vehicle approaches red");
        if (ped_walk_ns && ped_walk_ew)
            $fatal(1,"SAFETY FAILURE: both pedestrian phases active");
        if (fault_active &&
            (ns_light!=RED || ew_light!=RED || ped_walk_ns || ped_walk_ew))
            $fatal(1,"SAFETY FAILURE: unsafe outputs in fault state");
        if (ns_light==YELLOW && ew_light!=RED)
            $fatal(1,"SAFETY FAILURE: NS yellow overlaps EW non-red");
        if (ew_light==YELLOW && ns_light!=RED)
            $fatal(1,"SAFETY FAILURE: EW yellow overlaps NS non-red");
    end

    initial begin
        $dumpfile("advanced_traffic_management.vcd");
        $dumpvars(0,tb_advanced_traffic_management_controller);

        // Hold reset, then exercise startup all-red and normal operation.
        repeat (3) @(negedge clk);
        rst_n=1;
        repeat (150) begin
            @(negedge clk);
            ns_demand=$urandom_range(0,15);
            ew_demand=$urandom_range(0,15);
        end

        // Pulse requests for multiple cycles so the synchronizers can sample.
        ns_emergency_async=1; repeat(5) @(negedge clk); ns_emergency_async=0;
        repeat(80) @(negedge clk);
        ew_emergency_async=1; repeat(5) @(negedge clk); ew_emergency_async=0;
        repeat(80) @(negedge clk);

        ped_ns_async=1; repeat(5) @(negedge clk); ped_ns_async=0;
        ped_ew_async=1; repeat(5) @(negedge clk); ped_ew_async=0;
        repeat(120) @(negedge clk);

        // Simultaneous emergency requests exercise the documented tie policy.
        ns_emergency_async=1; ew_emergency_async=1;
        repeat(6) @(negedge clk);
        ns_emergency_async=0; ew_emergency_async=0;
        repeat(80) @(negedge clk);

        // Invalid sensor status must enter a latched all-red fault state.
        sensor_data_valid=0;
        repeat(5) @(negedge clk);
        if (!fault_active) $fatal(1,"FAIL: invalid sensor status did not latch fault");
        sensor_data_valid=1;
        repeat(10) @(negedge clk);
        if (!fault_active) $fatal(1,"FAIL: fault unexpectedly recovered without reset");

        $display("PASS: exercised traffic requests and output safety monitors.");
        $display("Inspect advanced_traffic_management.vcd. This is not formal proof or hardware certification.");
        $finish;
    end
endmodule
