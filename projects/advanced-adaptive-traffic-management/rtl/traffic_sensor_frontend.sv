`timescale 1ns/1ps
// Physical-input conditioning and low-cost demand estimator for a tabletop model.
// Vehicle sensors must provide pulses long enough to be sampled by clk; use an
// external pulse stretcher/toggle handshake for asynchronous narrow pulses.
module traffic_sensor_frontend #(
    parameter integer DEBOUNCE_CYCLES = 4,
    parameter integer DEMAND_DECAY_CYCLES = 1000
) (
    input  logic clk,
    input  logic rst_n,
    input  logic vehicle_ns_async,
    input  logic vehicle_ew_async,
    input  logic emergency_ns_async,
    input  logic emergency_ew_async,
    input  logic ped_ns_async,
    input  logic ped_ew_async,
    output logic [3:0] ns_demand,
    output logic [3:0] ew_demand,
    output logic emergency_ns,
    output logic emergency_ew,
    output logic pedestrian_ns,
    output logic pedestrian_ew,
    output logic sensor_frontend_healthy
);
    localparam integer DB_W = (DEBOUNCE_CYCLES < 2) ? 1 : $clog2(DEBOUNCE_CYCLES+1);
    localparam integer DECAY_W = (DEMAND_DECAY_CYCLES < 2) ? 1 : $clog2(DEMAND_DECAY_CYCLES+1);

    logic veh_ns_meta, veh_ns_sync, veh_ew_meta, veh_ew_sync;
    logic veh_ns_prev, veh_ew_prev;
    logic [DECAY_W-1:0] decay_counter;

    function automatic logic [3:0] sat_inc(input logic [3:0] value);
        sat_inc = (value == 4'hF) ? value : value + 1'b1;
    endfunction

    // Two-flop synchronizers for sampled vehicle sensor levels.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            veh_ns_meta <= 1'b0; veh_ns_sync <= 1'b0;
            veh_ew_meta <= 1'b0; veh_ew_sync <= 1'b0;
            veh_ns_prev <= 1'b0; veh_ew_prev <= 1'b0;
        end else begin
            veh_ns_meta <= vehicle_ns_async; veh_ns_sync <= veh_ns_meta;
            veh_ew_meta <= vehicle_ew_async; veh_ew_sync <= veh_ew_meta;
            veh_ns_prev <= veh_ns_sync; veh_ew_prev <= veh_ew_sync;
        end
    end

    // Stable-level debouncers for human-operated emergency/pedestrian buttons.
    traffic_button_debouncer #(.STABLE_CYCLES(DEBOUNCE_CYCLES)) u_em_ns
      (.clk(clk), .rst_n(rst_n), .async_in(emergency_ns_async), .stable_out(emergency_ns));
    traffic_button_debouncer #(.STABLE_CYCLES(DEBOUNCE_CYCLES)) u_em_ew
      (.clk(clk), .rst_n(rst_n), .async_in(emergency_ew_async), .stable_out(emergency_ew));
    traffic_button_debouncer #(.STABLE_CYCLES(DEBOUNCE_CYCLES)) u_ped_ns
      (.clk(clk), .rst_n(rst_n), .async_in(ped_ns_async), .stable_out(pedestrian_ns));
    traffic_button_debouncer #(.STABLE_CYCLES(DEBOUNCE_CYCLES)) u_ped_ew
      (.clk(clk), .rst_n(rst_n), .async_in(ped_ew_async), .stable_out(pedestrian_ew));

    // A coarse saturating demand score rises on vehicle events and slowly
    // decays after quiet periods. It is a teaching heuristic, not a calibrated
    // vehicle counter or safety-rated traffic detector.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ns_demand <= 4'd0;
            ew_demand <= 4'd0;
            decay_counter <= '0;
        end else begin
            if (veh_ns_sync && !veh_ns_prev) ns_demand <= sat_inc(ns_demand);
            if (veh_ew_sync && !veh_ew_prev) ew_demand <= sat_inc(ew_demand);

            if (decay_counter >= DEMAND_DECAY_CYCLES-1) begin
                decay_counter <= '0;
                if (!(veh_ns_sync && !veh_ns_prev) && ns_demand != 0)
                    ns_demand <= ns_demand - 1'b1;
                if (!(veh_ew_sync && !veh_ew_prev) && ew_demand != 0)
                    ew_demand <= ew_demand - 1'b1;
            end else begin
                decay_counter <= decay_counter + 1'b1;
            end
        end
    end

    // This indicates the conditioning block is out of reset. It is not proof
    // that external sensors are physically present or functioning correctly.
    always_comb sensor_frontend_healthy = rst_n;
endmodule

module traffic_button_debouncer #(
    parameter integer STABLE_CYCLES = 4
) (
    input logic clk,
    input logic rst_n,
    input logic async_in,
    output logic stable_out
);
    localparam integer COUNT_W = (STABLE_CYCLES < 2) ? 1 : $clog2(STABLE_CYCLES+1);
    logic meta, sync_in;
    logic [COUNT_W-1:0] stable_count;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            meta <= 1'b0;
            sync_in <= 1'b0;
            stable_out <= 1'b0;
            stable_count <= '0;
        end else begin
            meta <= async_in;
            sync_in <= meta;
            if (sync_in == stable_out) begin
                stable_count <= '0;
            end else if (stable_count >= STABLE_CYCLES-1) begin
                stable_out <= sync_in;
                stable_count <= '0;
            end else begin
                stable_count <= stable_count + 1'b1;
            end
        end
    end
endmodule
