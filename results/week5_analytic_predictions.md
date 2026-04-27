# Week-5 Analytic Predictions

Date: 2026-04-25

This report freezes the pre-scan algebraic predictions for the original and swapped Hamiltonian splits. The table is intentionally separate from numerical outcomes so the reduced-grid scans test predictions rather than define them.

Detailed hand derivations are in `results/week5_analytic_derivations.md`.

| observable | Split I algebraic class | Split II algebraic class | prediction change? |
|---|---|---|---|
| `h_hop_density` | sensitive | second-layer state-sensitive | **yes** |
| `electric_density` | state-suppressed blind | sensitive | **yes** |
| `staggered_magnetization` | state-suppressed blind | sensitive | **yes** |
| `mass_density` | state-suppressed blind | sensitive | **yes** |
| `total_energy_density` | sensitive | sensitive | **no** |

Centerpiece prediction:

Physically natural Hamiltonian regroupings move observables between algebraic classes, and numerical visibility should track the class rather than the observable identity.

Important refinement:

`h_hop_density` is not predicted to become fully blind under Split II. It moves from leading-defect sensitive to the second-layer state-sensitive class: `[O,H_A]=0`, but `[H_A,[H_B,O]]` is nonzero and has nonzero product-state expectation in the current check.
