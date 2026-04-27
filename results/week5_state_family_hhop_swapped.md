# Week-5 State-Family Probe: Swapped `h_hop_density`

Date: 2026-04-25

Purpose: test whether suppression for the swapped-split `H_A = H_hop` ground state is special to the exact ground state, generic along simple state families, or mostly caused by `O_hop` being proportional to `H_A`.

Observable and split:

- observable: `h_hop_density`
- split: swapped, `H_A = H_hop`, `H_B = H_mass + H_electric`
- second-layer operator: `[H_A,[H_B,O]]`

State families:

- `ha_evolved`: `exp(-i tau H_A)|psi_seed>`
- `h_evolved`: `exp(-i tau H)|psi_seed>`
- `sector_ground_interp`: normalized interpolation between the product seed and the `H_A` ground state projected into the same Gauss sector

Correlation with observed leading first-order coefficient:

- initial `|<nested>|` vs `|a_1|`: log Pearson r=0.255 using 80 rows
- final-time `|<nested>|` vs `|a_1|`: log Pearson r=0.092 using 80 rows

Here `a_1` is obtained from a two-term fit `E_1(dt) ~= a_1 dt + a_2 dt^2` for first-order Trotter observable error.

Main readout:

- The global correlation is weak across all families. The second-layer expectation is not a standalone scalar predictor of the fitted error coefficient once the state is moved around by `H_A` or by the full Hamiltonian.
- The gauge-sector ground-state interpolation is still highly informative: as `lambda` approaches one, the nested expectation collapses and the first-vs-second observable distinction is suppressed even though the observable and split are unchanged.
- This means the `H_A` ground-state suppression is not merely a coding artifact, but it also should not be overstated as generic for every nearby or evolved state. The state/protocol layer is real.

Family summaries:

- `h_evolved`: nested range [2.189e+00, 8.000e+00], `|a_1|` range [3.930e-04, 7.419e-01], max initial Gauss deviation 4.441e-16
- `ha_evolved`: nested range [1.193e-01, 8.000e+00], `|a_1|` range [3.930e-04, 8.016e-01], max initial Gauss deviation 3.331e-16
- `sector_ground_interp`: nested range [8.250e-16, 8.040e+00], `|a_1|` range [6.651e-06, 6.552e-01], max initial Gauss deviation 2.220e-16

Selected rows:

| family | seed | parameter | t_final | nested initial | nested final | q1 | `|a_1|` | q2 | ratio E1/E2 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ha_evolved` | `neel_x` | 0 | 0.5 | 8.000e+00 | 3.665e+00 | 0.536 | 6.151e-01 | 2.157 | 18.8 |
| `ha_evolved` | `neel_x` | 0 | 1 | 8.000e+00 | 5.157e+00 | 1.083 | 3.498e-01 | 2.234 | 23.5 |
| `h_evolved` | `neel_x` | 0 | 0.5 | 8.000e+00 | 3.665e+00 | 0.536 | 6.151e-01 | 2.157 | 18.8 |
| `h_evolved` | `neel_x` | 0 | 1 | 8.000e+00 | 5.157e+00 | 1.083 | 3.498e-01 | 2.234 | 23.5 |
| `ha_evolved` | `neel_x` | 0.75 | 0.5 | 3.677e+00 | 9.720e-02 | 1.008 | 6.444e-01 | 2.288 | 133 |
| `ha_evolved` | `neel_x` | 0.75 | 1 | 3.677e+00 | 8.003e-01 | 1.108 | 2.866e-01 | 1.396 | 37 |
| `h_evolved` | `neel_x` | 0.75 | 0.5 | 4.026e+00 | 5.709e+00 | 0.899 | 5.690e-01 | 1.991 | 24.6 |
| `h_evolved` | `neel_x` | 0.75 | 1 | 4.026e+00 | 5.953e+00 | 0.965 | 4.654e-01 | 1.984 | 12.3 |
| `ha_evolved` | `neel_x` | 1 | 0.5 | 4.279e+00 | 4.657e-01 | 0.845 | 4.287e-01 | 2.113 | 41.4 |
| `ha_evolved` | `neel_x` | 1 | 1 | 4.279e+00 | 3.692e+00 | 1.008 | 5.761e-01 | 1.666 | 61.3 |
| `h_evolved` | `neel_x` | 1 | 0.5 | 5.157e+00 | 5.471e+00 | 0.867 | 5.102e-01 | 2.039 | 20.3 |
| `h_evolved` | `neel_x` | 1 | 1 | 5.157e+00 | 6.839e+00 | 1.149 | 6.848e-01 | 2.042 | 11.7 |
| `ha_evolved` | `neel_x` | 2 | 0.5 | 3.197e+00 | 2.258e+00 | 0.808 | 5.282e-01 | 2.584 | 227 |
| `ha_evolved` | `neel_x` | 2 | 1 | 3.197e+00 | 3.120e+00 | 1.117 | 7.438e-01 | 2.427 | 635 |
| `h_evolved` | `neel_x` | 2 | 0.5 | 6.839e+00 | 2.932e+00 | 0.753 | 5.861e-01 | 2.166 | 35.4 |
| `h_evolved` | `neel_x` | 2 | 1 | 6.839e+00 | 6.221e+00 | 0.600 | 9.043e-02 | 2.110 | 7.73 |
| `sector_ground_interp` | `neel_x` | 0 | 0.5 | 8.000e+00 | 3.665e+00 | 0.536 | 6.151e-01 | 2.157 | 18.8 |
| `sector_ground_interp` | `neel_x` | 0 | 1 | 8.000e+00 | 5.157e+00 | 1.083 | 3.498e-01 | 2.234 | 23.5 |
| `sector_ground_interp` | `neel_x` | 0.75 | 0.5 | 2.760e+00 | 3.522e+00 | 1.497 | 6.940e-02 | 2.090 | 4.13 |
| `sector_ground_interp` | `neel_x` | 0.75 | 1 | 2.760e+00 | 2.517e-01 | 1.705 | 1.027e-01 | 2.124 | 1.67 |
| `sector_ground_interp` | `neel_x` | 0.9 | 0.5 | 9.548e-01 | 3.864e+00 | 1.838 | 1.617e-02 | 2.111 | 1.85 |
| `sector_ground_interp` | `neel_x` | 0.9 | 1 | 9.548e-01 | 4.022e-01 | 3.088 | 7.874e-02 | 2.136 | 0.112 |
| `sector_ground_interp` | `neel_x` | 1 | 0.5 | 8.250e-16 | 3.816e+00 | 2.123 | 5.041e-02 | 2.123 | 1 |
| `sector_ground_interp` | `neel_x` | 1 | 1 | 8.250e-16 | 6.366e-01 | 2.143 | 4.850e-02 | 2.143 | 1 |
| `ha_evolved` | `uniform_x` | 0 | 0.5 | 5.333e+00 | 2.760e+00 | 0.705 | 6.552e-01 | 2.187 | 48.5 |
| `ha_evolved` | `uniform_x` | 0 | 1 | 5.333e+00 | 3.357e+00 | 0.697 | 3.930e-04 | 2.214 | 9.42 |
| `h_evolved` | `uniform_x` | 0 | 0.5 | 5.333e+00 | 2.760e+00 | 0.705 | 6.552e-01 | 2.187 | 48.5 |
| `h_evolved` | `uniform_x` | 0 | 1 | 5.333e+00 | 3.357e+00 | 0.697 | 3.930e-04 | 2.214 | 9.42 |
| `ha_evolved` | `uniform_x` | 0.75 | 0.5 | 1.037e+00 | 2.476e-02 | 1.062 | 3.793e-01 | 2.905 | 624 |
| `ha_evolved` | `uniform_x` | 0.75 | 1 | 1.037e+00 | 1.503e+00 | 0.930 | 7.719e-01 | 2.020 | 38.2 |
| `h_evolved` | `uniform_x` | 0.75 | 0.5 | 2.773e+00 | 2.609e+00 | 0.438 | 1.208e-01 | 2.170 | 9.46 |
| `h_evolved` | `uniform_x` | 0.75 | 1 | 2.773e+00 | 3.693e+00 | 1.012 | 3.862e-01 | 1.945 | 22.8 |
| `ha_evolved` | `uniform_x` | 1 | 0.5 | 2.536e+00 | 1.433e+00 | 1.004 | 5.162e-01 | 1.517 | 186 |
| `ha_evolved` | `uniform_x` | 1 | 1 | 2.536e+00 | 2.040e+00 | 0.888 | 8.016e-01 | 2.025 | 41.9 |
| `h_evolved` | `uniform_x` | 1 | 0.5 | 3.357e+00 | 2.189e+00 | 0.726 | 1.196e-02 | 2.139 | 7.73 |
| `h_evolved` | `uniform_x` | 1 | 1 | 3.357e+00 | 5.037e+00 | 1.291 | 7.498e-02 | 1.956 | 2.12 |
| `ha_evolved` | `uniform_x` | 2 | 0.5 | 2.809e+00 | 1.064e+00 | 0.743 | 1.605e-01 | 2.638 | 184 |
| `ha_evolved` | `uniform_x` | 2 | 1 | 2.809e+00 | 3.392e+00 | 0.969 | 6.380e-01 | 1.786 | 222 |
| `h_evolved` | `uniform_x` | 2 | 0.5 | 5.037e+00 | 3.460e+00 | 0.748 | 7.419e-01 | 2.131 | 39.9 |
| `h_evolved` | `uniform_x` | 2 | 1 | 5.037e+00 | 2.933e+00 | 0.172 | 2.748e-01 | 2.172 | 18.1 |

Interpretation:

This diagnostic separates the structural fact `O_hop proportional H_A` from the state question. All rows share the same swapped split and observable, so changes in `|<nested>|` and in the observed leading coefficient are caused by the state family rather than by changing the observable.

Generated data:

- `results/week5_state_family_hhop_swapped.csv`
- `results/figures/week5_state_family_hhop_swapped.svg`
