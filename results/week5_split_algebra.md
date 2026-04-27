# Week-5 Split Algebra Classifier

Date: 2026-04-25

This is the pre-scan algebraic check for the proposed split-dependence story. It uses dense operators at `n_sites=3`, `j=1`, `g=1`, `m=0.5`; exact zero/nonzero operator identities should be size-independent for these local sums, but this is still a numerical algebra check rather than a proof.

Splits:

- `original`: H_A = H_mass + H_electric; H_B = H_hop
- `swapped`: H_A = H_hop; H_B = H_mass + H_electric
- `electric_isolated`: H_A = H_electric; H_B = H_mass + H_hop
- `mass_isolated`: H_A = H_mass; H_B = H_electric + H_hop

| split | observable | ||[O,H_A]|| | ||[H_A,[H_B,O]]|| | max product-state expectation | class |
|---|---|---:|---:|---:|---|
| `original` | `h_hop_density` | 1.131e+01 | 0.000e+00 | 0.000e+00 | **leading-defect sensitive** |
| `original` | `electric_density` | 0.000e+00 | 2.263e+01 | 0.000e+00 | **state-suppressed blind** |
| `original` | `staggered_magnetization` | 0.000e+00 | 3.695e+01 | 0.000e+00 | **state-suppressed blind** |
| `original` | `mass_density` | 0.000e+00 | 1.848e+01 | 0.000e+00 | **state-suppressed blind** |
| `original` | `total_energy_density` | 1.131e+01 | 3.919e+01 | 0.000e+00 | **leading-defect sensitive** |
| `swapped` | `h_hop_density` | 0.000e+00 | 3.200e+01 | 8.000e+00 | **algebraically suppressed but state-sensitive** |
| `swapped` | `electric_density` | 9.238e+00 | 0.000e+00 | 0.000e+00 | **leading-defect sensitive** |
| `swapped` | `staggered_magnetization` | 1.306e+01 | 0.000e+00 | 0.000e+00 | **leading-defect sensitive** |
| `swapped` | `mass_density` | 6.532e+00 | 0.000e+00 | 0.000e+00 | **leading-defect sensitive** |
| `swapped` | `total_energy_density` | 1.131e+01 | 3.200e+01 | 8.000e+00 | **leading-defect sensitive** |
| `electric_isolated` | `h_hop_density` | 9.238e+00 | 1.306e+01 | 0.000e+00 | **leading-defect sensitive** |
| `electric_isolated` | `electric_density` | 0.000e+00 | 1.848e+01 | 0.000e+00 | **state-suppressed blind** |
| `electric_isolated` | `staggered_magnetization` | 0.000e+00 | 2.613e+01 | 0.000e+00 | **state-suppressed blind** |
| `electric_isolated` | `mass_density` | 0.000e+00 | 1.306e+01 | 0.000e+00 | **state-suppressed blind** |
| `electric_isolated` | `total_energy_density` | 9.238e+00 | 1.848e+01 | 0.000e+00 | **leading-defect sensitive** |
| `mass_isolated` | `h_hop_density` | 6.532e+00 | 1.306e+01 | 0.000e+00 | **leading-defect sensitive** |
| `mass_isolated` | `electric_density` | 0.000e+00 | 1.306e+01 | 0.000e+00 | **state-suppressed blind** |
| `mass_isolated` | `staggered_magnetization` | 0.000e+00 | 2.613e+01 | 0.000e+00 | **state-suppressed blind** |
| `mass_isolated` | `mass_density` | 0.000e+00 | 1.306e+01 | 0.000e+00 | **state-suppressed blind** |
| `mass_isolated` | `total_energy_density` | 6.532e+00 | 1.306e+01 | 0.000e+00 | **leading-defect sensitive** |

Immediate readout:

- `h_hop_density`: `original`=leading-defect sensitive; `swapped`=algebraically suppressed but state-sensitive; `electric_isolated`=leading-defect sensitive; `mass_isolated`=leading-defect sensitive
- `electric_density`: `original`=state-suppressed blind; `swapped`=leading-defect sensitive; `electric_isolated`=state-suppressed blind; `mass_isolated`=state-suppressed blind
- `staggered_magnetization`: `original`=state-suppressed blind; `swapped`=leading-defect sensitive; `electric_isolated`=state-suppressed blind; `mass_isolated`=state-suppressed blind
- `mass_density`: `original`=state-suppressed blind; `swapped`=leading-defect sensitive; `electric_isolated`=state-suppressed blind; `mass_isolated`=state-suppressed blind
- `total_energy_density`: `original`=leading-defect sensitive; `swapped`=leading-defect sensitive; `electric_isolated`=leading-defect sensitive; `mass_isolated`=leading-defect sensitive
