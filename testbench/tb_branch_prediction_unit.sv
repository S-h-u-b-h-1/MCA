`timescale 1ns/1ps
`default_nettype none
// Final integrated BPU contract regression, parameterized across BHT/BTB sizes.
module tb_branch_prediction_unit;
    parameter integer INDEX_BITS = 4;
    localparam [31:0] PC_A = 32'h00001000;
    localparam [31:0] PC_B = 32'h00001004;
    localparam [31:0] PC_ALIAS = PC_A + (32'd4 << INDEX_BITS);
    localparam [31:0] TARGET_A = 32'h00002000;
    localparam [31:0] TARGET_B = 32'h00003000;
    localparam [31:0] TARGET_ALIAS = 32'h00004000;

    reg clk = 0;
    always #5 clk = ~clk;
    reg reset = 1;
    reg [31:0] fetch_pc = PC_A;
    wire predicted_taken;
    wire [1:0] prediction_state;
    wire btb_hit;
    wire [31:0] predicted_target, predicted_next_pc;

    reg resolve_valid = 0;
    reg [31:0] resolve_pc = 0;
    reg resolve_predicted_taken = 0;
    reg resolve_btb_hit = 0;
    reg [31:0] resolve_predicted_target = 0;
    reg resolve_actual_taken = 0;
    reg [31:0] resolve_actual_target = 0;
    wire mispredict, flush, redirect;
    wire [31:0] redirect_pc, selected_next_pc;
    reg saved_taken, saved_hit;
    reg [31:0] saved_target;
    integer checks = 0;
    integer failures = 0;

    branch_prediction_unit #(.INDEX_BITS(INDEX_BITS)) dut (
        .clk(clk), .reset(reset), .fetch_pc(fetch_pc),
        .predicted_taken(predicted_taken), .prediction_state(prediction_state),
        .btb_hit(btb_hit), .predicted_target(predicted_target),
        .predicted_next_pc(predicted_next_pc),
        .resolve_valid(resolve_valid), .resolve_pc(resolve_pc),
        .resolve_predicted_taken(resolve_predicted_taken),
        .resolve_btb_hit(resolve_btb_hit),
        .resolve_predicted_target(resolve_predicted_target),
        .resolve_actual_taken(resolve_actual_taken),
        .resolve_actual_target(resolve_actual_target),
        .mispredict(mispredict), .flush(flush), .redirect(redirect),
        .redirect_pc(redirect_pc), .selected_next_pc(selected_next_pc)
    );

    task check;
        input condition;
        input [8*120-1:0] label;
        begin
            checks = checks + 1;
            if (condition !== 1'b1) begin
                failures = failures + 1;
                $display("FAIL [%0d] %0s", checks, label);
                $display("  fetch=%h state=%b taken=%b hit=%b target=%h next=%h",
                         fetch_pc, prediction_state, predicted_taken, btb_hit,
                         predicted_target, predicted_next_pc);
                $display("  valid=%b mis=%b flush=%b redirect=%b rpc=%h selected=%h",
                         resolve_valid, mispredict, flush, redirect, redirect_pc,
                         selected_next_pc);
            end
        end
    endtask

    task fetch_at;
        input [31:0] pc;
        begin
            @(negedge clk);
            fetch_pc = pc;
            #1;
            saved_taken = predicted_taken;
            saved_hit = btb_hit;
            saved_target = predicted_target;
        end
    endtask

    task resolve_saved;
        input valid_branch;
        input [31:0] pc;
        input taken;
        input [31:0] actual_target;
        input expected_wrong;
        input [31:0] expected_redirect;
        begin
            @(negedge clk);
            resolve_valid = valid_branch;
            resolve_pc = pc;
            resolve_predicted_taken = saved_taken;
            resolve_btb_hit = saved_hit;
            resolve_predicted_target = saved_target;
            resolve_actual_taken = taken;
            resolve_actual_target = actual_target;
            #1;
            check(mispredict === expected_wrong, "direction/target misprediction flag");
            check(flush === expected_wrong && redirect === expected_wrong,
                  "flush and redirect are valid gated");
            check(redirect_pc === (expected_wrong ? expected_redirect : 32'd0),
                  "redirect address is resolved next PC");
            check(selected_next_pc === (expected_wrong ? expected_redirect : predicted_next_pc),
                  "recovery has priority over current fetch");
            @(posedge clk);
            #1;  // Nonblocking BHT/BTB updates have settled.
            resolve_valid = 0;
            #1;
            check(mispredict === 0 && flush === 0 && redirect === 0 && redirect_pc === 0,
                  "resolution signals deactivate");
        end
    endtask

    task reset_unit;
        begin
            @(negedge clk);
            resolve_valid = 0;
            reset = 1;
            @(posedge clk);
            #1;
            @(negedge clk);
            reset = 0;
        end
    endtask

    initial begin
        $dumpfile("results/bpu_integration.vcd");
        $dumpvars(0, tb_branch_prediction_unit);
        repeat (2) @(posedge clk);
        @(negedge clk);
        reset = 0;

        fetch_at(PC_A);
        check(prediction_state === 2'b01 && predicted_taken === 0,
              "cold start is weakly not taken");
        check(btb_hit === 0 && predicted_target === 0 &&
              predicted_next_pc === PC_A + 4, "cold BTB miss falls through");

        resolve_saved(1, PC_A, 1, TARGET_A, 1, TARGET_A);
        fetch_at(PC_A);
        check(prediction_state === 2'b10 && predicted_taken === 1,
              "taken outcome trains direction");
        check(btb_hit === 1 && predicted_target === TARGET_A &&
              predicted_next_pc === TARGET_A, "taken outcome trains BTB");

        resolve_saved(1, PC_A, 1, TARGET_A, 0, 0);
        fetch_at(PC_A);
        check(prediction_state === 2'b11 && predicted_next_pc === TARGET_A,
              "correct taken prediction strengthens state");

        resolve_saved(1, PC_A, 1, TARGET_B, 1, TARGET_B);
        fetch_at(PC_A);
        check(btb_hit === 1 && predicted_target === TARGET_B &&
              predicted_next_pc === TARGET_B, "wrong target is retrained");

        resolve_saved(1, PC_A, 0, 0, 1, PC_A + 4);
        fetch_at(PC_A);
        check(prediction_state === 2'b10 && btb_hit === 1 &&
              predicted_target === TARGET_B, "not taken does not pollute BTB");

        resolve_saved(1, PC_A, 0, 0, 1, PC_A + 4);
        fetch_at(PC_A);
        check(prediction_state === 2'b01 && predicted_taken === 0 &&
              predicted_next_pc === PC_A + 4, "second NT switches direction");

        fetch_at(PC_B);
        check(prediction_state === 2'b01 && btb_hit === 0,
              "independent branch index is cold");
        resolve_saved(0, PC_B, 1, TARGET_ALIAS, 0, 0);
        fetch_at(PC_B);
        check(prediction_state === 2'b01 && btb_hit === 0,
              "squashed branch cannot train BHT or BTB");

        reset_unit();
        fetch_at(PC_A);
        resolve_saved(1, PC_A, 1, TARGET_A, 1, TARGET_A);
        fetch_at(PC_A);
        resolve_saved(1, PC_A, 1, TARGET_A, 0, 0);

        fetch_at(PC_ALIAS);
        check(predicted_taken === 1 && btb_hit === 0 &&
              predicted_next_pc === PC_ALIAS + 4,
              "tagged BTB rejects alias, though BHT direction aliases");
        resolve_saved(1, PC_ALIAS, 1, TARGET_ALIAS, 1, TARGET_ALIAS);

        fetch_at(PC_A);
        check(predicted_taken === 1 && btb_hit === 0 &&
              predicted_next_pc === PC_A + 4,
              "BTB collision replaces prior tag");
        resolve_saved(1, PC_A, 1, TARGET_A, 1, TARGET_A);
        fetch_at(PC_A);
        check(btb_hit === 1 && predicted_target === TARGET_A,
              "target cache recovers from tagged miss");

        fetch_at(PC_A);
        fetch_pc = PC_B;  // Different speculative fetch while older A resolves.
        #1;
        resolve_saved(1, PC_A, 0, 0, 1, PC_A + 4);
        fetch_at(PC_B);
        check(prediction_state === 2'b01 && btb_hit === 0,
              "concurrent older resolution does not train new fetch index");

        reset_unit();
        fetch_at(PC_A);
        check(prediction_state === 2'b01 && predicted_taken === 0 &&
              btb_hit === 0 && predicted_next_pc === PC_A + 4,
              "synchronous reset clears both tables");

        $display("BPU INDEX_BITS=%0d: %0d checks, %0d failures",
                 INDEX_BITS, checks, failures);
        if (failures != 0) $fatal(1, "BPU integration regression failed");
        $display("ALL BPU INTEGRATION TESTS PASSED (%0d checks)", checks);
        $finish;
    end
endmodule
`default_nettype wire
