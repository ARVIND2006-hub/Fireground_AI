`timescale 1ns/1ps
// Advanced educational RTL prototype with request queues and fail-safe state.
// Encodings: vehicle lights 00=RED, 01=YELLOW, 10=GREEN.
// This is a design-study project, NOT a certified traffic controller.
module advanced_traffic_management_controller #(
    parameter integer GREEN_MIN_CYCLES = 8,
    parameter integer GREEN_MAX_CYCLES = 64,
    parameter integer GREEN_SCALE      = 4,
    parameter integer YELLOW_CYCLES    = 4,
    parameter integer ALL_RED_CYCLES   = 2,
    parameter integer PED_WALK_CYCLES  = 16
) (
    input  logic       clk,
    input  logic       rst_n,

    // Demand inputs are assumed synchronous to clk and already conditioned.
    input  logic [3:0] ns_demand,
    input  logic [3:0] ew_demand,
    input  logic       sensor_data_valid,

    // Asynchronous request inputs; use pulse stretching/handshake upstream
    // if pulses may be shorter than two clock periods.
    input  logic       ns_emergency_async,
    input  logic       ew_emergency_async,
    input  logic       ped_ns_async,
    input  logic       ped_ew_async,

    output logic [1:0] ns_light,
    output logic [1:0] ew_light,
    output logic       ped_walk_ns,
    output logic       ped_walk_ew,
    output logic       emergency_active,
    output logic       fault_active,
    output logic [3:0] debug_state,
    output logic [7:0] debug_timer
);
    localparam logic [1:0] RED=2'b00, YELLOW=2'b01, GREEN=2'b10;
    localparam integer MAX_PHASE_CYCLES =
        (GREEN_MAX_CYCLES > PED_WALK_CYCLES) ?
        ((GREEN_MAX_CYCLES > YELLOW_CYCLES) ?
         ((GREEN_MAX_CYCLES > ALL_RED_CYCLES) ? GREEN_MAX_CYCLES : ALL_RED_CYCLES) :
         ((YELLOW_CYCLES > ALL_RED_CYCLES) ? YELLOW_CYCLES : ALL_RED_CYCLES)) :
        ((PED_WALK_CYCLES > YELLOW_CYCLES) ?
         ((PED_WALK_CYCLES > ALL_RED_CYCLES) ? PED_WALK_CYCLES : ALL_RED_CYCLES) :
         ((YELLOW_CYCLES > ALL_RED_CYCLES) ? YELLOW_CYCLES : ALL_RED_CYCLES));
    localparam integer TIMER_W = (MAX_PHASE_CYCLES < 2) ? 1 : $clog2(MAX_PHASE_CYCLES + 1);

    typedef enum logic [3:0] {
        ST_STARTUP_RED, ST_NS_GREEN, ST_NS_YELLOW, ST_EW_GREEN,
        ST_EW_YELLOW, ST_ALL_RED, ST_PED_NS, ST_PED_EW, ST_FAULT
    } state_t;

    state_t state, next_state;
    logic [TIMER_W-1:0] timer;
    logic [TIMER_W-1:0] green_limit;

    logic ns_em_meta, ns_em_sync, ew_em_meta, ew_em_sync;
    logic ped_ns_meta, ped_ns_sync, ped_ew_meta, ped_ew_sync;
    logic ns_em_prev, ew_em_prev, ped_ns_prev, ped_ew_prev;
    logic ns_em_pending, ew_em_pending, ped_ns_pending, ped_ew_pending;
    logic last_green_ns;

    function automatic logic [TIMER_W-1:0] green_cycles(input logic [3:0] demand);
        integer value;
        begin
            value = GREEN_MIN_CYCLES + (demand * GREEN_SCALE);
            if (value > GREEN_MAX_CYCLES) value = GREEN_MAX_CYCLES;
            if (value < GREEN_MIN_CYCLES) value = GREEN_MIN_CYCLES;
            green_cycles = value[TIMER_W-1:0];
        end
    endfunction

    // Synchronize asynchronous controls. This reduces (but does not eliminate)
    // metastability risk; external pulse capture requirements still apply.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ns_em_meta <= 0; ns_em_sync <= 0;
            ew_em_meta <= 0; ew_em_sync <= 0;
            ped_ns_meta <= 0; ped_ns_sync <= 0;
            ped_ew_meta <= 0; ped_ew_sync <= 0;
            ns_em_prev <= 0; ew_em_prev <= 0;
            ped_ns_prev <= 0; ped_ew_prev <= 0;
        end else begin
            ns_em_meta <= ns_emergency_async; ns_em_sync <= ns_em_meta;
            ew_em_meta <= ew_emergency_async; ew_em_sync <= ew_em_meta;
            ped_ns_meta <= ped_ns_async; ped_ns_sync <= ped_ns_meta;
            ped_ew_meta <= ped_ew_async; ped_ew_sync <= ped_ew_meta;
            ns_em_prev <= ns_em_sync; ew_em_prev <= ew_em_sync;
            ped_ns_prev <= ped_ns_sync; ped_ew_prev <= ped_ew_sync;
        end
    end

    // Edge-capture request queues. A request stays pending until served.
    // Requests arriving on the same cycle as service are retained only if a
    // new rising edge is detected after the synchronized input has gone low.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ns_em_pending <= 0; ew_em_pending <= 0;
            ped_ns_pending <= 0; ped_ew_pending <= 0;
        end else begin
            if (ns_em_sync && !ns_em_prev) ns_em_pending <= 1;
            else if ((state == ST_ALL_RED) && (next_state == ST_NS_GREEN)) ns_em_pending <= 0;

            if (ew_em_sync && !ew_em_prev) ew_em_pending <= 1;
            else if ((state == ST_ALL_RED) && (next_state == ST_EW_GREEN)) ew_em_pending <= 0;

            if (ped_ns_sync && !ped_ns_prev) ped_ns_pending <= 1;
            else if (state == ST_PED_NS) ped_ns_pending <= 0;

            if (ped_ew_sync && !ped_ew_prev) ped_ew_pending <= 1;
            else if (state == ST_PED_EW) ped_ew_pending <= 0;
        end
    end

    // Priority policy at each all-red decision:
    // 1) single pending emergency; 2) simultaneous emergencies alternate
    //    using last_green_ns; 3) pedestrian requests; 4) larger demand;
    // 5) alternate roads on equal demand.
    always_comb begin
        next_state = state;
        case (state)
            ST_STARTUP_RED:
                if (timer >= ALL_RED_CYCLES-1) next_state = ST_NS_GREEN;

            ST_NS_GREEN:
                if ((ew_em_pending && !ns_em_pending) ||
                    (!ns_em_pending && timer >= green_limit-1))
                    next_state = ST_NS_YELLOW;

            ST_NS_YELLOW:
                if (timer >= YELLOW_CYCLES-1) next_state = ST_ALL_RED;

            ST_EW_GREEN:
                if ((ns_em_pending && !ew_em_pending) ||
                    (!ew_em_pending && timer >= green_limit-1))
                    next_state = ST_EW_YELLOW;

            ST_EW_YELLOW:
                if (timer >= YELLOW_CYCLES-1) next_state = ST_ALL_RED;

            ST_ALL_RED: begin
                if (!sensor_data_valid) next_state = ST_FAULT;
                else if (timer >= ALL_RED_CYCLES-1) begin
                    if (ns_em_pending && ew_em_pending)
                        next_state = last_green_ns ? ST_EW_GREEN : ST_NS_GREEN;
                    else if (ns_em_pending) next_state = ST_NS_GREEN;
                    else if (ew_em_pending) next_state = ST_EW_GREEN;
                    else if (ped_ns_pending) next_state = ST_PED_NS;
                    else if (ped_ew_pending) next_state = ST_PED_EW;
                    else if (ns_demand > ew_demand) next_state = ST_NS_GREEN;
                    else if (ew_demand > ns_demand) next_state = ST_EW_GREEN;
                    else next_state = last_green_ns ? ST_EW_GREEN : ST_NS_GREEN;
                end
            end

            ST_PED_NS, ST_PED_EW:
                if (!sensor_data_valid) next_state = ST_FAULT;
                else if (timer >= PED_WALK_CYCLES-1) next_state = ST_ALL_RED;

            ST_FAULT: next_state = ST_FAULT;
            default: next_state = ST_FAULT;
        endcase

        // Invalid sensor status is fail-safe from every operating phase.
        if (!sensor_data_valid && state != ST_FAULT)
            next_state = ST_FAULT;
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= ST_STARTUP_RED;
            timer <= '0;
            green_limit <= GREEN_MIN_CYCLES[TIMER_W-1:0];
            last_green_ns <= 1'b1;
        end else begin
            if ((state == ST_NS_GREEN) && (next_state == ST_NS_YELLOW))
                last_green_ns <= 1'b1;
            else if ((state == ST_EW_GREEN) && (next_state == ST_EW_YELLOW))
                last_green_ns <= 1'b0;

            if (state != next_state) begin
                state <= next_state;
                timer <= '0;
                if (next_state == ST_NS_GREEN) green_limit <= green_cycles(ns_demand);
                else if (next_state == ST_EW_GREEN) green_limit <= green_cycles(ew_demand);
            end else if (timer < MAX_PHASE_CYCLES[TIMER_W-1:0]) begin
                timer <= timer + 1'b1;
            end
        end
    end

    // Moore outputs: startup, all-red, and fault default to all vehicle red.
    always_comb begin
        ns_light = RED;
        ew_light = RED;
        ped_walk_ns = 1'b0;
        ped_walk_ew = 1'b0;
        emergency_active = ns_em_pending | ew_em_pending | ns_em_sync | ew_em_sync;
        fault_active = (state == ST_FAULT);
        debug_state = state;
        debug_timer = timer; // zero-extend or truncate to the 8-bit debug port

        case (state)
            ST_NS_GREEN:  begin ns_light = GREEN; ew_light = RED; end
            ST_NS_YELLOW: begin ns_light = YELLOW; ew_light = RED; end
            ST_EW_GREEN:  begin ns_light = RED; ew_light = GREEN; end
            ST_EW_YELLOW: begin ns_light = RED; ew_light = YELLOW; end
            ST_PED_NS:    ped_walk_ns = 1'b1;
            ST_PED_EW:    ped_walk_ew = 1'b1;
            default: begin end
        endcase
    end
endmodule
