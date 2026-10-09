`timescale 1ns/1ps

// Advanced educational traffic controller.
// Road-light encoding: 00=RED, 01=YELLOW, 10=GREEN.
// Pedestrian walk outputs are asserted only while both roads are RED.
// Emergency and pedestrian inputs are synchronized internally.
// Demand inputs are 4-bit encoded values and must be stable/synchronized externally.
module adaptive_traffic_controller_advanced #(
    parameter integer GREEN_MIN_CYCLES = 4,
    parameter integer GREEN_MAX_CYCLES = 20,
    parameter integer GREEN_SCALE       = 2,
    parameter integer YELLOW_CYCLES     = 3,
    parameter integer ALL_RED_CYCLES    = 2,
    parameter integer PED_WALK_CYCLES   = 8
) (
    input  logic       clk,
    input  logic       rst_n,
    input  logic [3:0] north_south_demand,
    input  logic [3:0] east_west_demand,
    input  logic       ns_emergency_async,
    input  logic       ew_emergency_async,
    input  logic       ped_cross_ns_async,
    input  logic       ped_cross_ew_async,
    input  logic       sensor_data_valid,

    output logic [1:0] ns_light,
    output logic [1:0] ew_light,
    output logic       ped_walk_ns,
    output logic       ped_walk_ew,
    output logic       emergency_active,
    output logic       fault_active
);
    localparam logic [1:0] RED = 2'b00, YELLOW = 2'b01, GREEN = 2'b10;

    typedef enum logic [3:0] {
        S_NS_GREEN, S_NS_YELLOW, S_EW_GREEN, S_EW_YELLOW,
        S_ALL_RED, S_PED_NS, S_PED_EW, S_FAULT
    } state_t;

    state_t state, next_state;

    logic ns_emergency_meta, ns_emergency_sync;
    logic ew_emergency_meta, ew_emergency_sync;
    logic ped_ns_meta, ped_ns_sync;
    logic ped_ew_meta, ped_ew_sync;

    logic ped_ns_pending, ped_ew_pending;
    logic last_green_was_ns;
    integer timer;
    integer green_limit;

    function automatic integer calculate_green(input logic [3:0] demand);
        integer result;
        begin
            result = GREEN_MIN_CYCLES + (demand * GREEN_SCALE);
            if (result > GREEN_MAX_CYCLES)
                calculate_green = GREEN_MAX_CYCLES;
            else
                calculate_green = result;
        end
    endfunction

    // Two-flop synchronizers for asynchronous control inputs.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ns_emergency_meta <= 1'b0;
            ns_emergency_sync <= 1'b0;
            ew_emergency_meta <= 1'b0;
            ew_emergency_sync <= 1'b0;
            ped_ns_meta       <= 1'b0;
            ped_ns_sync       <= 1'b0;
            ped_ew_meta       <= 1'b0;
            ped_ew_sync       <= 1'b0;
        end else begin
            ns_emergency_meta <= ns_emergency_async;
            ns_emergency_sync <= ns_emergency_meta;
            ew_emergency_meta <= ew_emergency_async;
            ew_emergency_sync <= ew_emergency_meta;
            ped_ns_meta       <= ped_cross_ns_async;
            ped_ns_sync       <= ped_ns_meta;
            ped_ew_meta       <= ped_cross_ew_async;
            ped_ew_sync       <= ped_ew_meta;
        end
    end

    // Latch pedestrian requests until their crossing phase is serviced.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ped_ns_pending <= 1'b0;
            ped_ew_pending <= 1'b0;
        end else begin
            if (ped_ns_sync)
                ped_ns_pending <= 1'b1;
            else if (state == S_PED_NS)
                ped_ns_pending <= 1'b0;

            if (ped_ew_sync)
                ped_ew_pending <= 1'b1;
            else if (state == S_PED_EW)
                ped_ew_pending <= 1'b0;
        end
    end

    // Next-state logic. Invalid sensor data enters a latched fail-safe state;
    // recovery requires reset after the input data is valid again.
    always_comb begin
        next_state = state;

        if (!sensor_data_valid && state != S_FAULT) begin
            next_state = S_FAULT;
        end else begin
            case (state)
                S_NS_GREEN: begin
                    if ((ew_emergency_sync && !ns_emergency_sync) ||
                        (!ns_emergency_sync && timer >= green_limit-1))
                        next_state = S_NS_YELLOW;
                end

                S_NS_YELLOW:
                    if (timer >= YELLOW_CYCLES-1)
                        next_state = S_ALL_RED;

                S_EW_GREEN: begin
                    if ((ns_emergency_sync && !ew_emergency_sync) ||
                        (!ew_emergency_sync && timer >= green_limit-1))
                        next_state = S_EW_YELLOW;
                end

                S_EW_YELLOW:
                    if (timer >= YELLOW_CYCLES-1)
                        next_state = S_ALL_RED;

                S_ALL_RED: begin
                    if (timer >= ALL_RED_CYCLES-1) begin
                        if (ew_emergency_sync && !ns_emergency_sync)
                            next_state = S_EW_GREEN;
                        else if (ns_emergency_sync && !ew_emergency_sync)
                            next_state = S_NS_GREEN;
                        else if (ped_ns_pending)
                            next_state = S_PED_NS;
                        else if (ped_ew_pending)
                            next_state = S_PED_EW;
                        else if (north_south_demand > east_west_demand)
                            next_state = S_NS_GREEN;
                        else if (east_west_demand > north_south_demand)
                            next_state = S_EW_GREEN;
                        else if (last_green_was_ns)
                            next_state = S_EW_GREEN;
                        else
                            next_state = S_NS_GREEN;
                    end
                end

                S_PED_NS, S_PED_EW:
                    if (timer >= PED_WALK_CYCLES-1)
                        next_state = S_ALL_RED;

                S_FAULT: next_state = S_FAULT;
                default: next_state = S_FAULT;
            endcase
        end
    end

    // State, timer, and adaptive green-time register.
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state             <= S_NS_GREEN;
            timer             <= 0;
            green_limit       <= GREEN_MIN_CYCLES;
            last_green_was_ns <= 1'b1;
        end else begin
            if ((state == S_NS_GREEN) && (next_state == S_NS_YELLOW))
                last_green_was_ns <= 1'b1;
            else if ((state == S_EW_GREEN) && (next_state == S_EW_YELLOW))
                last_green_was_ns <= 1'b0;

            if (state != next_state) begin
                state <= next_state;
                timer <= 0;
                if (next_state == S_NS_GREEN)
                    green_limit <= calculate_green(north_south_demand);
                else if (next_state == S_EW_GREEN)
                    green_limit <= calculate_green(east_west_demand);
            end else begin
                timer <= timer + 1;
            end
        end
    end

    // Safe output decode: fault, all-red and pedestrian phases keep vehicles red.
    always_comb begin
        ns_light       = RED;
        ew_light       = RED;
        ped_walk_ns    = 1'b0;
        ped_walk_ew    = 1'b0;
        emergency_active = ns_emergency_sync | ew_emergency_sync;
        fault_active   = (state == S_FAULT);

        case (state)
            S_NS_GREEN:  begin ns_light = GREEN;  ew_light = RED;    end
            S_NS_YELLOW: begin ns_light = YELLOW; ew_light = RED;    end
            S_EW_GREEN:  begin ns_light = RED;    ew_light = GREEN;  end
            S_EW_YELLOW: begin ns_light = RED;    ew_light = YELLOW; end
            S_PED_NS:    begin ped_walk_ns = 1'b1; end
            S_PED_EW:    begin ped_walk_ew = 1'b1; end
            default: begin end
        endcase
    end
endmodule
