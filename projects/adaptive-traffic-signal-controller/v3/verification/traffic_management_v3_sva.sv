// Bind or instantiate in an SVA-capable simulator.
// These properties check sampled output invariants; they do not prove the
// entire controller correct and must be run with suitable assumptions.
module traffic_management_v3_sva (
    input logic clk, rst_n,
    input logic [1:0] ns_light, ew_light,
    input logic ped_walk_ns, ped_walk_ew, fault_active
);
    localparam logic [1:0] RED=2'b00, GREEN=2'b10, YELLOW=2'b01;

    ap_no_conflicting_green:
        assert property (@(posedge clk) disable iff (!rst_n)
            !(ns_light==GREEN && ew_light==GREEN))
        else $error("Opposing approaches simultaneously green");

    ap_ns_yellow_excludes_ew:
        assert property (@(posedge clk) disable iff (!rst_n)
            ns_light==YELLOW |-> ew_light==RED)
        else $error("NS yellow while EW is not red");

    ap_ew_yellow_excludes_ns:
        assert property (@(posedge clk) disable iff (!rst_n)
            ew_light==YELLOW |-> ns_light==RED)
        else $error("EW yellow while NS is not red");

    ap_pedestrian_phase_safe:
        assert property (@(posedge clk) disable iff (!rst_n)
            (ped_walk_ns || ped_walk_ew) |->
            (ns_light==RED && ew_light==RED))
        else $error("Pedestrian walk while a vehicle approach is not red");

    ap_pedestrian_mutual_exclusion:
        assert property (@(posedge clk) disable iff (!rst_n)
            !(ped_walk_ns && ped_walk_ew))
        else $error("Both pedestrian directions enabled");

    ap_fault_is_all_red:
        assert property (@(posedge clk) disable iff (!rst_n)
            fault_active |-> (ns_light==RED && ew_light==RED &&
                              !ped_walk_ns && !ped_walk_ew))
        else $error("Fault state outputs are not fail-safe");
endmodule
