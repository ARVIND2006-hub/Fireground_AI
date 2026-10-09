`timescale 1ns/1ps
module tb_traffic_sensor_frontend;
    logic clk=0, rst_n=0;
    logic vehicle_ns_async=0, vehicle_ew_async=0;
    logic emergency_ns_async=0, emergency_ew_async=0;
    logic ped_ns_async=0, ped_ew_async=0;
    wire [3:0] ns_demand, ew_demand;
    wire emergency_ns, emergency_ew, pedestrian_ns, pedestrian_ew;
    wire sensor_frontend_healthy;

    traffic_sensor_frontend #(.DEBOUNCE_CYCLES(3), .DEMAND_DECAY_CYCLES(100))
      dut (.*);
    always #5 clk=~clk;

    task automatic pulse_ns;
      begin
        @(negedge clk); vehicle_ns_async=1;
        repeat(4) @(negedge clk);
        vehicle_ns_async=0;
        repeat(4) @(negedge clk);
      end
    endtask

    initial begin
        repeat(3) @(negedge clk); rst_n=1;
        if (!sensor_frontend_healthy) $fatal(1,"health output should be high after reset");
        pulse_ns();
        if (ns_demand !== 1) $fatal(1,"NS demand should increment once, got %0d",ns_demand);
        pulse_ns();
        if (ns_demand !== 2) $fatal(1,"NS demand should increment twice, got %0d",ns_demand);

        @(negedge clk); emergency_ns_async=1;
        repeat(8) @(negedge clk);
        if (!emergency_ns) $fatal(1,"emergency button was not debounced high");
        emergency_ns_async=0;
        repeat(8) @(negedge clk);
        if (emergency_ns) $fatal(1,"emergency button was not debounced low");

        @(negedge clk); ped_ew_async=1;
        repeat(8) @(negedge clk);
        if (!pedestrian_ew) $fatal(1,"pedestrian button was not debounced high");

        $display("PASS: sensor frontend debounce and demand smoke test.");
        $finish;
    end
endmodule
