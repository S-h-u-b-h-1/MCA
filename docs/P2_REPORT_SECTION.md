# P2: Tagged Branch Target Buffer (BTB)

**Author:** Tanish Yadav, Enrollment No. 2401010474, B.Tech CS and AI (3rd year), Newton School of Technology

## 1. Purpose
The branch history table (P1) predicts only the direction of a branch. The BTB
supplies the destination address of a taken branch, so the fetch stage can
redirect without waiting for decode. Source: `rtl/branch_target_buffer.v`.

## 2. Interface
| Signal | Dir | Width | Description |
|---|---|---|---|
| clk | in | 1 | Clock; all state changes on the rising edge |
| reset | in | 1 | Synchronous reset; clears all valid bits |
| lookup_pc | in | 32 | PC being looked up (combinational) |
| update_valid | in | 1 | Write enable. Must be asserted only for a resolved, taken branch |
| update_pc | in | 32 | PC of the resolved branch |
| update_target | in | 32 | Resolved target address |
| hit | out | 1 | 1 when the indexed entry is valid and its tag matches |
| target | out | 32 | Stored target when hit = 1, otherwise 0x00000000 |

Parameter: `INDEX_BITS` (default 4). Entries = 2^INDEX_BITS.

## 3. Organisation
Direct-mapped. Each entry holds a valid bit, a tag of (30 - INDEX_BITS) bits and a
32-bit target. With the default INDEX_BITS = 4 there are 16 entries, the tag is
PC[31:6] (26 bits), the index is PC[5:2] and PC[1:0] is ignored.

```
              lookup_pc[31:0]
                   |
        +----------+-----------+
        |                      |
   tag = PC[31:6]        index = PC[5:2]
        |                      |
        |             +--------v---------+
        |             | 16-entry table   |
        |             | valid | tag | tgt|
        |             +--+-----+-----+---+
        |                |     |     |
        |                |  +--v--+  |
        +----------------+->| ==  |  |
                         |  +--+--+  |
                      +--v--+  |     |
                      | AND |<-+     |
                      +--+--+        |
                         |        +--v---+
                        hit ----->| mux  |--> target (0 on miss)
                                  +------+
```

## 4. Behaviour (verified against the RTL)
- **Lookup** is combinational: `hit = valid[index] && (tag[index] == lookup_tag)`.
  The full tag is compared, so aliasing PCs never produce a false hit.
- **Update** is synchronous. On a rising edge with `update_valid = 1`, the valid
  bit, tag and target at the update index are written. A new branch that maps to
  an occupied index replaces the old entry.
- **Reset** is synchronous and clears only the valid bits. It has priority over
  `update_valid`. Tags and targets are not cleared.
- **Same-cycle lookup and update:** the lookup returns the old state before the
  clock edge and the new state after it.
- **Power-up:** valid bits have no initial value, so `hit` is unknown until the
  first clock edge with `reset = 1`.

## 5. Verification
All results were produced by `make test-btb`, `make test-bpu` and
`make synth-btb-checked`, using Icarus Verilog 13.0 and Yosys 0.70.
- Default 16-entry testbench (`tb_btb.sv`): 17 checks passed, 0 failed.
- Parameterised testbench (`tb_btb_param.sv`): 23 checks (4 entries), 59 checks
  (16 entries) and 107 checks (32 entries) passed, 0 failed. Covers reset
  priority, all entries with unique targets, disabled updates, tag collision,
  same-cycle lookup/update, target replacement and reset recovery.
- Integrated predictor (`make test-bpu`): 70 checks, 0 failures, for INDEX_BITS 4 and 5.
- A failing check calls `$fatal`, so make exits nonzero. This was verified by
  deliberately breaking one expected value (exit code 2).
- Yosys generic synthesis with `check -assert`: 0 problems. The default
  configuration maps to 2404 generic cells (928 enable flip-flops, 16 plain
  flip-flops). These are technology-independent cells, not FPGA resources.
- Waveform: `evidence/waveforms/btb.png`. It shows a cold miss, a hit with the
  correct target, the 0x100 / 0x140 collision and replacement, and a target
  change from 0x300 to 0x350. Logs: `evidence/btb_logs/` and `evidence/btb_final/`.

## 6. Integration contract
The BTB does not know whether a branch was taken. The resolution logic must
assert `update_valid` only for a valid, resolved, taken branch that should be
trained, with `update_pc` set to the branch PC and `update_target` to the
resolved target. The fetch logic uses `hit` to decide whether `target` is usable.
If the predicted target is wrong, the pipeline redirects to the resolved PC.

## 7. Limitations
- Direct-mapped: PCs that share an index evict each other.
- Timing is unmeasured. No FPGA target or place-and-route report exists yet; see
  `docs/TIMING_FEASIBILITY.md`. No frequency is claimed.
- The simulation clock in the testbenches (10 ns period) is a simulation
  convention and is not a performance figure.

## 8. Additional evidence
`evidence/waveforms/bpu_btb.png` shows the BTB inside the integrated predictor (`make test-bpu`): a cold miss, hits with trained targets 0x2000 and 0x3000, mispredict/redirect recovery, and `failures` = 0 throughout.
