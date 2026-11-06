# P5 generic synthesis evidence

Tool: `Yosys 0.33 (git sha1 2584903a060)`.

Command: `make synth-all`. Each top runs in a separate Yosys process with
`hierarchy -check`, `synth -flatten`, `check -assert`, and default RTL parameters.
All 7 synthesis/check commands succeeded in this run.

| RTL top | Generic cells after flattening |
| --- | ---: |
| `predictor_2bit` | 162 |
| `predictor_1bit` | 88 |
| `branch_target_buffer` | 2498 |
| `next_pc_mux` | 112 |
| `branch_resolution` | 214 |
| `predictor_top` | 227 |
| `branch_prediction_unit` | 2993 |

These are generic logic/register cells, not FPGA LUT counts. No device, clock
constraint, placement/routing or timing analysis is included; maximum MHz is unmeasured.
Counts are not additive across tops. `predictor_top` combines direction predictors only;
`branch_prediction_unit` integrates BHT/BTB/recovery RTL but is not a complete CPU.

Raw logs, netlists, tool version, per-type counts and RTL SHA-256 hashes: `results/synthesis/`.
Generated results are ignored by Git; reproduce locally or download the CI artifact.
