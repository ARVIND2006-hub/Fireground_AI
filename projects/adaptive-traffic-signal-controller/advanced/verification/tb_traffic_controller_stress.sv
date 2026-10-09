`timescale 1ns/1ps

// Directed + pseudo-random stress test for the advanced controller.
// This is simulation-based checking, not a replacement for formal verification.
module tb_traffic_controller_stress;
    logic clk = 0, rst_n = 0;
    logic [3:0] north_south_demand = 0, east_west_demand = 0;
    logic ns_emergency_async = 0, ew_emergency_async = 0;
    logic ped_cross_ns_async = 0, ped_cross_ew_async = 0;
    logic sensor_data_valid = 1;
    logic [1:0] ns_light, ew_light;
    logic ped_walk_ns, ped_walk_ew, emergency_active, fault_active;

    localparam logic [1:0] RED = 2'b00, GREEN = 2'b10;
    integer cycle;

    adaptive_traffic_controller_advanced #(
        .GREEN_MIN_CYCLES(4), .GREEN_MAX_CYCLES(20),
        .GREEN_SCALE(2), .YELLOW_CYCLES(3),
        .ALL_RED_CYCLES(2), .PED_WALK_CYCLES(8)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .north_south_demand(north_south_demand),
        .east_west_demand(east_west_demand),
        .ns_emergency_async(ns_emergency_async),
        .ew_emergency_async(ew_emergency_async),
        .ped_cross_ns_async(ped_cross_ns_async),
        .ped_cross_ew_async(ped_cross_ew_async),
        .sensor_data_valid(sensor_data_valid),
        .ns_light(ns_light), .ew_light(ew_light),
        .ped_walk_ns(ped_walk_ns), .ped_walk_ew(ped_walk_ew),
        .emergency_active(emergency_active), .fault_active(fault_active)
    );

    always #5 clk = ~clk;

    always @(negedge clk) begin
        if (rst_n) begin
            if (ns_light == GREEN && ew_light == GREEN)
                $fatal(1, "SAFETY FAIL: conflicting green outputs at cycle %0d", cycle);
            if ((ped_walk_ns || ped_walk_ew) &&
                (ns_light != RED || ew_light != RED))
                $fatal(1, "SAFETY FAIL: pedestrian walk without both vehicle approaches red");
            if (ped_walk_ns && ped_walk_ew)
                $fatal(1, "SAFETY FAIL: both pedestrian crossings enabled");
            if (fault_active &&
                (ns_light != RED || ew_light != RED || ped_walk_ns || ped_walk_ew))
                $fatal(1, "SAFETY FAIL: unsafe output in fault mode");
        end
    end

    initial begin
        $dumpfile("traffic_controller_stress.vcd");
        $dumpvars(0, tb_traffic_controller_stress);
        cycle = 0;
        repeat (3) @(negedge clk);
        rst_n = 1;

        // Deterministic pseudo-random stress: vary demand and pulse requests.
        for (cycle = 0; cycle < 600; cycle = cycle + 1) begin
            @(negedge clk);
            north_south_demand = $urandom_range(0, 15);
            east_west_demand   = $urandom_range(0, 15);

            // Short multi-cycle requests so the synchronizer can observe them.
            ns_emergency_async = ($urandom_range(0, 39) == 0);
            ew_emergency_async = ($urandom_range(0, 43) == 0);
            ped_cross_ns_async = ($urandom_range(0, 17) == 0);
            ped_cross_ew_async = ($urandom_range(0, 19) == 0);

            // Exercise invalid sensor status, then restore it. Fault is expected
            // to remain latched until reset, so keep this scenario at the end.
            sensor_data_valid = 1'b1;
        end

        ns_emergency_async = 0;
        ew_emergency_async = 0;
        ped_cross_ns_async = 0;
        ped_cross_ew_async = 0;

        // Separate fail-safe test: invalid sensor data must latch fault mode.
        repeat (3) @(negedge clk);
        sensor_data_valid = 0;
        repeat (4) @(negedge clk);
        if (!fault_active)
            $fatal(1, "FAIL: fault mode did not activate on invalid sensor status");
        sensor_data_valid = 1;
        repeat (4) @(negedge clk);
        if (!fault_active)
            $fatal(1, "FAIL: fault mode did not remain latched");

        $display("PASS: 600-cycle stress run and fail-safe checks completed.");
        $display("This result is meaningful only when observed in a simulator run.");
        $finish;
    end
endmodule
