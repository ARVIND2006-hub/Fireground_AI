`timescale 1ns/1ps
module tb_traffic_watchdog;
    logic clk=0, rst_n=0, heartbeat=0, sensor_data_valid=1, clear_fault=0;
    wire watchdog_fault;
    wire [31:0] heartbeat_age;
    traffic_watchdog #(.TIMEOUT_CYCLES(12)) dut (.*);
    always #5 clk=~clk;

    task automatic beat;
      begin
        @(negedge clk); heartbeat=1;
        repeat(3) @(negedge clk);
        heartbeat=0;
        repeat(3) @(negedge clk);
      end
    endtask

    initial begin
        repeat(3) @(negedge clk); rst_n=1;
        beat();
        if (watchdog_fault) $fatal(1,"watchdog faulted despite heartbeat");
        repeat(20) @(negedge clk);
        if (!watchdog_fault) $fatal(1,"watchdog did not time out");
        sensor_data_valid=0;
        @(negedge clk);
        if (!watchdog_fault) $fatal(1,"invalid sensor status should latch fault");
        sensor_data_valid=1;
        clear_fault=1;
        beat();
        repeat(2) @(negedge clk);
        clear_fault=0;
        $display("PASS: watchdog timeout and sensor-health smoke test completed.");
        $finish;
    end
endmodule
