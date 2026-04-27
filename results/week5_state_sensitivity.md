# Week-5 State-Sensitivity Probe

Date: 2026-04-25

Target observable and split:

- observable: `h_hop_density`
- split: swapped, `H_A = H_hop`, `H_B = H_mass + H_electric`
- algebraic class: second-layer state-sensitive (`[O,H_A]=0`, but `[H_A,[H_B,O]]` is nonzero)

Protocol:

- `n_sites=3`
- `g=1.0`, `j=1.0`, `m=0.5`
- `t_final={0.5,1.0}`
- `dt={0.5,0.25,0.125,0.0625}`

States compared:

- product states: `neel_x`, `uniform_x`
- split ground state: `split_a_ground`, the ground state of `H_A` under the swapped split, i.e. the ground state of `H_hop`

## Numerical Readout

Product-state probe:

- data: `results/week5_probe_swapped_h_hop_density_scan.csv`
- fits: `results/week5_probe_swapped_h_hop_density_fits.csv`
- summary: `results/week5_probe_swapped_h_hop_density_summary.txt`
- numerical class in reduced table: sensitive
- reduced-table metrics: `dq=1.443`, median `E1/E2=21.2`

Split-`H_A` ground-state probe:

- data: `results/week5_swapped_h_hop_density_split_a_ground_scan.csv`
- fits: `results/week5_swapped_h_hop_density_split_a_ground_fits.csv`
- summary: `results/week5_swapped_h_hop_density_split_a_ground_summary.txt`

| state | t_final | trotter1 observable fit | trotter2 observable fit | readout |
|---|---:|---:|---:|---|
| `split_a_ground` | 0.5 | `7.495e-01 * dt^2.122` | `7.495e-01 * dt^2.122` | observable-level method distinction suppressed |
| `split_a_ground` | 1.0 | `6.230e-01 * dt^2.136` | `6.230e-01 * dt^2.136` | observable-level method distinction suppressed |

For the same runs, state error still distinguishes the integrators:

| state | t_final | trotter1 state-error fit | trotter2 state-error fit |
|---|---:|---:|---:|
| `split_a_ground` | 0.5 | `9.422e-01 * dt^1.033` | `7.364e-01 * dt^2.116` |
| `split_a_ground` | 1.0 | `9.583e-01 * dt^1.036` | `6.480e-01 * dt^2.108` |

## Interpretation

This is the cleanest evidence so far that the second layer is real. The observable is not simply "sensitive" or "blind" as an identity. Under the swapped split, `h_hop_density` is algebraically protected at the leading commutator layer, but its numerical visibility depends on the state/protocol.

For product states on the reduced grid, the observable remains numerically sensitive. For the physically motivated `H_A` ground state, the observable-level first- and second-order errors become indistinguishable even though the state-level errors still show the expected integrator-order separation.

This supports the revised centerpiece:

Physically natural Hamiltonian regroupings move observables between algebraic classes, and numerical visibility tracks the class rather than the observable identity.
