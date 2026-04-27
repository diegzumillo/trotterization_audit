# Week-5 n=4 Anchor Reproduction

Date: 2026-04-25

Purpose: check whether the swapped-split `h_hop_density` anchor effect survives one size larger than the main reduced-grid `n_sites=3` runs.

## Protocol

```text
n_sites = 4
g = 1.0
j = 1.0
m = 0.5
observable = h_hop_density
split = swapped, H_A = H_hop, H_B = H_mass + H_electric
t_final = 0.5, 1.0
dt = 0.5, 0.25, 0.125, 0.0625
```

States:

- product states: `neel_x`, `uniform_x`
- split ground state: `split_a_ground`, the ground state of `H_A = H_hop`

Artifacts:

- product scan: `results/week5_n4_swapped_h_hop_density_product_scan.csv`
- product fits: `results/week5_n4_swapped_h_hop_density_product_fits.csv`
- product summary: `results/week5_n4_swapped_h_hop_density_product_summary.txt`
- `H_A` ground-state scan: `results/week5_n4_swapped_h_hop_density_split_a_ground_scan.csv`
- `H_A` ground-state fits: `results/week5_n4_swapped_h_hop_density_split_a_ground_fits.csv`
- `H_A` ground-state summary: `results/week5_n4_swapped_h_hop_density_split_a_ground_summary.txt`

## Product-State Readout

| state | t_final | trotter1 observable fit | trotter2 observable fit |
|---|---:|---:|---:|
| `neel_x` | 0.5 | `1.781e-01 * dt^0.533` | `7.063e-01 * dt^2.155` |
| `neel_x` | 1.0 | `3.044e-01 * dt^1.017` | `4.963e-01 * dt^2.218` |
| `uniform_x` | 0.5 | `3.469e-01 * dt^0.784` | `1.010e-01 * dt^2.242` |
| `uniform_x` | 1.0 | `1.001e+00 * dt^2.929` | `9.695e-02 * dt^2.399` |

Aggregate product-state metrics:

- mean `q1 = 1.316`
- mean `q2 = 2.254`
- `dq = 0.938`
- median small-`dt` `E1/E2 = 17.2`

Readout: product states remain observably method-sensitive at `n=4`.

## `H_A` Ground-State Readout

| state | t_final | trotter1 observable fit | trotter2 observable fit | readout |
|---|---:|---:|---:|---|
| `split_a_ground` | 0.5 | `3.278e-01 * dt^2.048` | `3.278e-01 * dt^2.048` | observable-level method distinction suppressed |
| `split_a_ground` | 1.0 | `3.968e-01 * dt^2.004` | `3.968e-01 * dt^2.004` | observable-level method distinction suppressed |

Aggregate `H_A` ground-state metrics:

- mean `q1 = 2.026`
- mean `q2 = 2.026`
- `dq ~= 0`
- median small-`dt` `E1/E2 = 1.0`

For the same state, state error still distinguishes first- and second-order Trotter:

| state | t_final | trotter1 state-error fit | trotter2 state-error fit |
|---|---:|---:|---:|
| `split_a_ground` | 0.5 | `1.068e+00 * dt^1.057` | `7.240e-01 * dt^2.064` |
| `split_a_ground` | 1.0 | `1.014e+00 * dt^1.035` | `7.859e-01 * dt^2.037` |

## Conclusion

The anchor effect reproduces at `n=4`: under the swapped split, product states show observable-level method sensitivity for `h_hop_density`, while the `H_A = H_hop` ground state suppresses the observable-level first-vs-second distinction. This strengthens the claim that the intermediate class is a real state/protocol layer rather than an `n=3` artifact.
