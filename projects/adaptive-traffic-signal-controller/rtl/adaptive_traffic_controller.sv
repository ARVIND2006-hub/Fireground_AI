`timescale 1ns/1ps

// Educational two-road adaptive traffic signal controller.
// Light encoding: 00=RED, 01=YELLOW, 10=GREEN.
module adaptive_traffic_controller #(
    parameter integer GREEN_MIN_CYCLES = 4,
    parameter integer GREEN_MAX_CYCLES = 12,
    parameter integer YELLOW_CYCLES    = 2,
    parameter integer ALL_RED_CYCLES   = 1
) (
    input  logic       clk,
    input  logic       rst_n,
    input  logic [3:0] north_south_count,
    input  logic [3:0] east_west_count,
    input  logic       ns_emergency,
    input  logic       ew_emergency,
    output logic [1:0] ns_light,
    output logic [1:0] ew_light,
    output logic       emergency_mode
);
    localparam logic [1:0] RED = 2'b00, YELLOW = 2'b01, GREEN = 2'b10;

    typedef enum logic [2:0] { NS_GREEN, NS_YELLOW, EW_GREEN, EW_YELLOW, ALL_RED } state_t;
    state_t state, next_state;

    integer timer;
    integer green_limit;
    logic last_green_was_ns;

    function automatic integer demand_to_green_limit(input logic [3:0] demand);
        integer calculated;
        begin
            calculated = GREEN_MIN_CYCLES + demand;
            if (calculated > GREEN_MAX_CYCLES)
                demand_to_green_limit = GREEN_MAX_CYCLES;
            else
                demand_to_green_limit = calculated;
        end
    endfunction

    always_comb begin
        next_state = state;
        case (state)
            NS_GREEN: begin
                if ((ew_emergency && !ns_emergency) ||
                    (!ns_emergency && timer >= green_limit-1))
                    next_state = NS_YELLOW;
            end
            NS_YELLOW: if (timer >= YELLOW_CYCLES-1) next_state = ALL_RED;
            EW_GREEN: begin
                if ((ns_emergency && !ew_emergency) ||
                    (!ew_emergency && timer >= green_limit-1))
                    next_state = EW_YELLOW;
            end
            EW_YELLOW: if (timer >= YELLOW_CYCLES-1) next_state = ALL_RED;
            ALL_RED: begin
                if (timer >= ALL_RED_CYCLES-1) begin
                    if (ew_emergency && !ns_emergency)
                        next_state = EW_GREEN;
                    else if (ns_emergency && !ew_emergency)
                        next_state = NS_GREEN;
                    else if (last_green_was_ns)
                        next_state = EW_GREEN;
                    else
                        next_state = NS_GREEN;
                end
            end
            default: next_state = NS_GREEN;
        endcase
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state              <= NS_GREEN;
            timer              <= 0;
            green_limit        <= GREEN_MIN_CYCLES;
            last_green_was_ns  <= 1'b1;
            emergency_mode     <= 1'b0;
        end else begin
            emergency_mode <= ns_emergency | ew_emergency;

            if ((state == NS_GREEN) && (next_state == NS_YELLOW))
                last_green_was_ns <= 1'b1;
            else if ((state == EW_GREEN) && (next_state == EW_YELLOW))
                last_green_was_ns <= 1'b0;

            if (state != next_state) begin
                state <= next_state;
                timer <= 0;
                if (next_state == NS_GREEN)
                    green_limit <= demand_to_green_limit(north_south_count);
                else if (next_state == EW_GREEN)
                    green_limit <= demand_to_green_limit(east_west_count);
            end else begin
                timer <= timer + 1;
            end
        end
    end

    always_comb begin
        ns_light = RED;
        ew_light = RED;
        case (state)
            NS_GREEN:  begin ns_light = GREEN;  ew_light = RED;    end
            NS_YELLOW: begin ns_light = YELLOW; ew_light = RED;    end
            EW_GREEN:  begin ns_light = RED;    ew_light = GREEN;  end
            EW_YELLOW: begin ns_light = RED;    ew_light = YELLOW; end
            default:   begin ns_light = RED;    ew_light = RED;    end
        endcase
    end
endmodule
