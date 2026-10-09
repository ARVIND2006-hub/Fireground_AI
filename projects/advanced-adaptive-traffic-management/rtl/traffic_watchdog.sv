`timescale 1ns/1ps
// Sticky health monitor for a model SoC. A missing heartbeat or invalid sensor
// status latches a fault until reset. This is diagnostic RTL, not a certified
// safety mechanism and is not wired into the traffic output path by default.
module traffic_watchdog #(
    parameter integer TIMEOUT_CYCLES = 1000
) (
    input logic clk,
    input logic rst_n,
    input logic heartbeat,
    input logic sensor_data_valid,
    input logic clear_fault,
    output logic watchdog_fault,
    output logic [31:0] heartbeat_age
);
    logic heartbeat_meta, heartbeat_sync, heartbeat_prev;
    localparam integer AGE_W = (TIMEOUT_CYCLES < 2) ? 1 : $clog2(TIMEOUT_CYCLES+1);

    logic [AGE_W-1:0] age_counter;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            heartbeat_meta <= 1'b0;
            heartbeat_sync <= 1'b0;
            heartbeat_prev <= 1'b0;
            age_counter <= '0;
            heartbeat_age <= 32'd0;
            watchdog_fault <= 1'b0;
        end else begin
            heartbeat_meta <= heartbeat;
            heartbeat_sync <= heartbeat_meta;
            heartbeat_prev <= heartbeat_sync;

            if (heartbeat_sync && !heartbeat_prev) begin
                age_counter <= '0;
                heartbeat_age <= 32'd0;
            end else if (age_counter < TIMEOUT_CYCLES) begin
                age_counter <= age_counter + 1'b1;
                heartbeat_age <= heartbeat_age + 1'b1;
            end else begin
                watchdog_fault <= 1'b1;
            end

            if (!sensor_data_valid) watchdog_fault <= 1'b1;
            if (clear_fault && sensor_data_valid &&
                (heartbeat_sync != heartbeat_prev))
                watchdog_fault <= 1'b0;
        end
    end
endmodule
