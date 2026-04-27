# Week-5 Full Report: Split-Dependent Observable Reliability

Date: 2026-04-25

Manuscript status: `template.tex` was not edited during this phase. This report consolidates the week-5 analytic and numerical work so the manuscript can be revised later from a stable evidence base.

## Executive Summary

The original paper was too modest because it treated observable reliability mostly as a binary property: some observables appeared sensitive to Trotter defects, while others appeared blind. Week 5 expands the story into a stronger and more defensible claim:

**Physically natural Hamiltonian regroupings move observables between algebraic classes, and numerical visibility tracks the class rather than the observable identity.**

The key outcome is not a simple sensitive-to-blind flip. The more interesting result is that the intermediate class is real. In particular, `h_hop_density` is leading-defect sensitive in the original split, but under the swapped split it becomes **second-layer state-sensitive**: `[O,H_A]=0`, while `[H_A,[H_B,O]]` is nonzero. Product states still show observable-level sensitivity, but the ground state of the swapped `H_A = H_hop` suppresses the observable-level distinction between first- and second-order Trotter while state error still distinguishes the integrators.

This gives the revised paper a clearer conceptual center:

- the classification procedure has more than two classes;
- the class depends on the Hamiltonian split;
- the second layer depends on the state/protocol and is numerically visible;
- gauge preservation alone is still not enough to guarantee reliable observable dynamics.

## Context From the Paper

The current manuscript already argues that local gauge preservation does not automatically imply accurate observable dynamics under Trotterized time evolution. The previous center of gravity was the contrast between observables such as `h_hop_density` and observables such as staggered magnetization or electric density under one fixed split:

```text
Split I / original:
H_A = H_mass + H_electric
H_B = H_hop
```

That produced a useful but limited message: some observables are sensitive and others are blind. The weakness is that the claim can look empirical and split-specific.

Week 5 reframes this as an algebraic classification problem. Given a split `H = H_A + H_B`, an observable `O`, and an initial state `|psi>`, the reliability class is not an intrinsic label attached to `O`. It is a property of `(O, split, state/protocol)`.

## Model and Observables

The toy Hamiltonian is

```text
H = H_mass + H_electric + H_hop
H_mass     = m sum_x (-1)^x Z_x
H_electric = g sum_x X_l
H_hop      = -j sum_x X_x Z_l X_{x+1}
```

Matter sites carry Pauli operators `X_x, Z_x`; links carry `X_l, Z_l`. Operators on different qubits commute. On the same qubit, `X` and `Z` anticommute.

The five observables used throughout are:

```text
O_hop   = H_hop / n
O_elec  = H_electric / n
O_stag  = (1/n) sum_x (-1)^x Z_x
O_mass  = H_mass / n
O_total = H / n
```

## Classification Procedure

For a chosen split `H = H_A + H_B`, classify an observable as follows:

1. If `[O,H_A] != 0`, classify it as **leading-defect sensitive**.
2. If `[O,H_A] = 0` but `[H_A,[H_B,O]] != 0`, classify it as **second-layer state-sensitive**.
3. If both operator tests vanish, classify it as **fully blind** at this order.
4. If the second-layer operator is nonzero but its expectation vanishes for the states tested, the practical numerical class is **state-suppressed blind** for that protocol.

This is the important shift from the old binary story. The second layer is not a technicality; it is the main new result.

## Splits Tested

The original split is

```text
H_A = H_mass + H_electric
H_B = H_hop
```

The main alternative split is the swapped split:

```text
H_A = H_hop
H_B = H_mass + H_electric
```

Additional split catalog entries exist in the code (`electric_isolated`, `mass_isolated`), but the week-5 report focuses on original vs swapped because this is the cleanest conceptual comparison and the right scope before scaling up.

## Analytic Predictions

The hand derivations are in `results/week5_analytic_derivations.md`; the frozen prediction table is in `results/week5_analytic_predictions.md`.

The central Pauli-commutator facts are:

- `H_hop` contains matter `X_x`, so it fails to commute with matter-`Z` observables such as `O_stag` and `O_mass`.
- `H_hop` contains link `Z_l`, so it fails to commute with link-`X` observables such as `O_elec`.
- `O_hop` is proportional to `H_hop`, so it commutes with `H_hop` but not generally with `H_mass + H_electric`.
- `O_total = H/n`, so `[O_total,H_A] = [H_B,H_A]/n`, nonzero for noncommuting split pieces.

Analytic prediction table:

| observable | Split I class | Split II class | change? |
|---|---|---|---|
| `h_hop_density` | leading-defect sensitive | second-layer state-sensitive | yes |
| `electric_density` | state-suppressed blind | leading-defect sensitive | yes |
| `staggered_magnetization` | state-suppressed blind | leading-defect sensitive | yes |
| `mass_density` | state-suppressed blind | leading-defect sensitive | yes |
| `total_energy_density` | leading-defect sensitive | leading-defect sensitive | no |

The most important correction to the original roadmap is the first row. `h_hop_density` does not become fully blind under the swapped split. It moves into the intermediate class.

## Numerical Protocol

The reduced-grid validation protocol was:

```text
n_sites = 3
g = 1.0
j = 1.0
m = 0.5
states = neel_x, uniform_x
t_final = 0.5, 1.0
dt = 0.5, 0.25, 0.125, 0.0625
splits = original, swapped
```

The numerical classification uses the same week-4 diagnostic style:

- `dq = q2 - q1`, where `q1` and `q2` are fitted observable-error slopes for first- and second-order Trotter.
- `ratio E1/E2` is the median small-`dt` observable-error ratio.
- A large positive `dq` and large ratio indicate numerical sensitivity to integrator order.
- Near-zero `dq` and ratio near one indicate numerical blindness under the tested protocol.

The reduced-grid scan artifacts are:

- `results/week5_probe_original_swapped_table.md`
- `results/week5_probe_original_swapped_table.csv`
- per-observable scan, fit, and summary CSV/TXT files under `results/week5_probe_original_*` and `results/week5_probe_swapped_*`

## Reduced-Grid Numerical Results

| observable | original | swapped |
|---|---:|---:|
| `h_hop_density` | **sensitive**; `dq=1.214`; ratio `113` | **sensitive**; `dq=1.443`; ratio `21.2` |
| `electric_density` | **blind**; `dq=-0.000`; ratio `1` | **blind**; `dq=-0.060`; ratio `0.687` |
| `staggered_magnetization` | **blind**; `dq=-0.000`; ratio `1` | **blind**; `dq=-0.046`; ratio `0.884` |
| `mass_density` | **blind**; `dq=-0.000`; ratio `1` | **blind**; `dq=-0.046`; ratio `0.884` |
| `total_energy_density` | **sensitive**; `dq=0.749`; ratio `12.3` | **sensitive**; `dq=0.781`; ratio `9.85` |

This table is deliberately modest. It shows that operator-level leading sensitivity is not automatically visible in the reduced product-state protocol. That is not a failure of the classification. It tells us the state/protocol layer matters.

## Algebra vs Numerical Visibility

The direct comparison table is in `results/week5_algebra_numeric_comparison.md`.

| observable | split | algebraic class | numerical class | dq | ratio E1/E2 | readout |
|---|---|---|---|---:|---:|---|
| `h_hop_density` | `original` | sensitive | **sensitive** | 1.214 | 113 | aligned |
| `h_hop_density` | `swapped` | second-layer state-sensitive | **sensitive** | 1.443 | 21.2 | visible beyond leading class |
| `electric_density` | `original` | state-suppressed blind | **blind** | -0.000 | 1 | aligned |
| `electric_density` | `swapped` | sensitive | **blind** | -0.060 | 0.687 | state/protocol suppressed |
| `staggered_magnetization` | `original` | state-suppressed blind | **blind** | -0.000 | 1 | aligned |
| `staggered_magnetization` | `swapped` | sensitive | **blind** | -0.046 | 0.884 | state/protocol suppressed |
| `mass_density` | `original` | state-suppressed blind | **blind** | -0.000 | 1 | aligned |
| `mass_density` | `swapped` | sensitive | **blind** | -0.046 | 0.884 | state/protocol suppressed |
| `total_energy_density` | `original` | sensitive | **sensitive** | 0.749 | 12.3 | aligned |
| `total_energy_density` | `swapped` | sensitive | **sensitive** | 0.781 | 9.85 | aligned |

The main lesson is that the algebraic class gives the channel through which a Trotter defect can affect the observable, while the state and protocol determine whether that channel is visible in a particular scan.

## State-Sensitivity Probe

The second-layer experiment focuses on the most interesting observable:

```text
observable = h_hop_density
split = swapped
H_A = H_hop
H_B = H_mass + H_electric
```

Analytically:

```text
[O_hop, H_A] = 0
[H_A, [H_B, O_hop]] != 0
```

Therefore `h_hop_density` is second-layer state-sensitive under the swapped split.

The state-sensitivity probe compares:

- product states: `neel_x`, `uniform_x`;
- `split_a_ground`: the ground state of the swapped `H_A`, i.e. the ground state of `H_hop`.

The product-state probe remains numerically sensitive:

```text
dq = 1.443
median E1/E2 = 21.2
```

For the `H_hop` ground state, the observable-level distinction is suppressed:

| state | t_final | trotter1 observable fit | trotter2 observable fit | readout |
|---|---:|---:|---:|---|
| `split_a_ground` | 0.5 | `7.495e-01 * dt^2.122` | `7.495e-01 * dt^2.122` | observable-level method distinction suppressed |
| `split_a_ground` | 1.0 | `6.230e-01 * dt^2.136` | `6.230e-01 * dt^2.136` | observable-level method distinction suppressed |

For the same state, state error still distinguishes the integrators:

| state | t_final | trotter1 state-error fit | trotter2 state-error fit |
|---|---:|---:|---:|
| `split_a_ground` | 0.5 | `9.422e-01 * dt^1.033` | `7.364e-01 * dt^2.116` |
| `split_a_ground` | 1.0 | `9.583e-01 * dt^1.036` | `6.480e-01 * dt^2.108` |

This is the cleanest week-5 evidence that the middle class is real. The observable itself is not simply reliable or unreliable. Its numerical reliability depends on the split and state.

## n=4 Anchor Reproduction

The anchor effect was reproduced at `n_sites=4`; see `results/week5_n4_anchor_reproduction.md`.

For swapped-split `h_hop_density`, product states remain observably method-sensitive:

```text
mean q1 = 1.316
mean q2 = 2.254
dq = 0.938
median small-dt E1/E2 = 17.2
```

For the `H_A = H_hop` ground state, the observable-level distinction is again suppressed:

```text
mean q1 = 2.026
mean q2 = 2.026
dq ~= 0
median small-dt E1/E2 = 1.0
```

State error still distinguishes first- and second-order Trotter for the same `H_A` ground-state runs. This is the strongest numerical support so far that the middle class is not an `n=3` artifact.

## State-Family Follow-Up

The `H_hop` ground-state result raises an important question: is the suppression special to the exact `H_A` ground state, generic for nearby or low-energy `H_A` states, or simply caused by `O_hop` being proportional to `H_A`?

To test this, an additional state-family sweep was run for swapped-split `h_hop_density`. The report is in `results/week5_state_family_hhop_swapped.md`, the data are in `results/week5_state_family_hhop_swapped.csv`, and the scatter plot is in `results/figures/week5_state_family_hhop_swapped.svg`.

The tested families were:

- `ha_evolved`: `exp(-i tau H_A)|psi_seed>`;
- `h_evolved`: `exp(-i tau H)|psi_seed>`;
- `sector_ground_interp`: a normalized interpolation between the product seed and the `H_A` ground state projected into the same Gauss sector.

For each state, the diagnostic compares

```text
| < [H_A,[H_B,O]] > |
```

against an observed leading first-order coefficient `|a_1|` from

```text
E_1(dt) ~= a_1 dt + a_2 dt^2.
```

The global correlation is weak:

```text
initial |<nested>| vs |a_1|: r = 0.255
final-time |<nested>| vs |a_1|: r = 0.092
```

This is useful, not disappointing. It says the second-layer expectation is not a universal one-number predictor once states are moved around by `H_A` or by the full Hamiltonian. However, the sector-compatible ground-state interpolation does show the expected collapse near the projected `H_A` ground state: the nested expectation drops toward zero and the first-vs-second observable distinction is suppressed.

The interpretation is:

- `O_hop proportional H_A` makes leading protection possible under the swapped split.
- That structural protection is not sufficient by itself; product and evolved states can still show visible observable error.
- The `H_A` ground-state suppression is real, but it should be presented as a state/protocol effect rather than as generic behavior for all nearby states.

## Code Changes and Reproducibility

New or modified code files:

- `z2_trotter/splits.py`: named split catalog and split-term construction.
- `z2_trotter/__init__.py`: exports split helpers.
- `run_week2_scan.py`: accepts `--split`; supports `split_a_ground` initial state.
- `analyze_week5_split_algebra.py`: dense algebraic classifier.
- `build_week5_split_table.py`: builds split comparison tables from scan artifacts.
- `build_week5_prediction_report.py`: builds prediction and algebra-vs-numerics reports.
- `run_week5_state_family.py`: runs state-family diagnostics for swapped `h_hop_density`.

Main generated report artifacts:

- `results/week5_analytic_derivations.md`
- `results/week5_analytic_predictions.md`
- `results/week5_split_algebra.md`
- `results/week5_probe_original_swapped_table.md`
- `results/week5_algebra_numeric_comparison.md`
- `results/week5_state_sensitivity.md`
- `results/week5_state_family_hhop_swapped.md`
- `results/figures/week5_state_family_hhop_swapped.svg`
- `results/week5_n4_anchor_reproduction.md`
- `results/week5_reference_audit.md`
- `results/week5_numerical_workplan.md`

Representative commands:

```powershell
python analyze_week5_split_algebra.py
python build_week5_split_table.py --splits original,swapped --observables h_hop_density,electric_density,staggered_magnetization,mass_density,total_energy_density --artifact-prefix week5_probe --output-csv week5_probe_original_swapped_table.csv --output-md week5_probe_original_swapped_table.md
python build_week5_prediction_report.py
python run_week2_scan.py --split swapped --observable h_hop_density --n-sites 3 --g-values 1.0 --initial-states split_a_ground --t-finals 0.5,1.0 --dts 0.5,0.25,0.125,0.0625 --output results/week5_swapped_h_hop_density_split_a_ground_scan.csv --fit-output results/week5_swapped_h_hop_density_split_a_ground_fits.csv --summary results/week5_swapped_h_hop_density_split_a_ground_summary.txt --quiet
python run_week5_state_family.py
```

Validation performed:

```text
python -m py_compile run_week2_scan.py build_week5_split_table.py build_week5_prediction_report.py run_week5_state_family.py
```

## Implications for the Manuscript

The paper should be reframed around the classification procedure rather than around a fixed list of observables.

Suggested manuscript role for week-5 results:

1. Introduce the three-class procedure after the model section.
2. Present Split I as the baseline that reproduces the current observable-dependent sensitivity map.
3. Present Split II as the split-dependence test.
4. Use the analytic prediction table as the new conceptual Table I.
5. Use the algebra-vs-numerics table to show that operator-level sensitivity and numerical visibility are related but not identical.
6. Use the swapped `h_hop_density` state-sensitivity probe as the centerpiece example of the second layer.
7. Include the `n=4` anchor reproduction as the finite-size sanity check.
8. Retain the gauge-preservation argument as a separate point: gauge constraints can remain well behaved even when observable reliability depends on split and state.

Suggested new conceptual table:

| observable | Split I class | Split II class | numerical visibility | diagnosis |
|---|---|---|---|---|
| `h_hop_density` | leading sensitive | second-layer state-sensitive | sensitive/product, suppressed/`H_A`-ground | middle class anchor |
| `electric_density` | state-suppressed blind | leading sensitive | blind on product grid | protocol suppression |
| `staggered_magnetization` | state-suppressed blind | leading sensitive | blind on product grid | protocol suppression |
| `mass_density` | state-suppressed blind | leading sensitive | blind on product grid | protocol suppression |
| `total_energy_density` | leading sensitive | leading sensitive | sensitive | robust sensitive channel |

The key paper-level claim should be:

```text
Observable reliability under Trotterized gauge dynamics is a property of the observable, Hamiltonian split, and initial state/protocol. A lightweight commutator hierarchy predicts the relevant algebraic class, and numerical scans show that visibility follows this class structure rather than the observable identity alone.
```

For PRD/PRR positioning, the manuscript should also make the scope explicit:

```text
The commutator audit is a classificatory diagnostic. It identifies the algebraic channel through which Trotter defects can enter an observable, but it is not proposed as a universal quantitative estimator of the final observable-error prefactor.
```

PRD/PRR readiness checklist:

| item | status | note |
|---|---|---|
| `n=4` reproduction of anchor effect | done | `results/week5_n4_anchor_reproduction.md` |
| state-family figure | done | `results/figures/week5_state_family_hhop_swapped.svg` |
| cleaned references | pending | quick audit in `results/week5_reference_audit.md`; metadata cleanup still needed |
| classificatory-not-estimator statement | drafted | text above |
| manuscript rewrite | pending | wait until reference cleanup and final figure choice |

## What Not To Claim Yet

Do not claim that every operator-level sensitive observable becomes numerically sensitive on the reduced product-state grid. The swapped-split `electric_density`, `staggered_magnetization`, and `mass_density` rows show state/protocol suppression.

Do not claim that `h_hop_density` flips from sensitive to fully blind. The correct statement is stronger and more nuanced: it moves from leading-defect sensitive to second-layer state-sensitive.

Do not claim that the nested expectation alone predicts all observed prefactors. The state-family sweep shows weak global correlation, while still supporting the targeted ground-state suppression.

Do not expand to larger system sizes or more splits until the reporting and interpretation of this reduced-grid result are stable.

## Next Steps

The next numerical task is performance, not more physics scope. A full default dense swapped-split scan for one observable exceeded 120 seconds. Before running all splits and observables at larger grids, cache repeated exact evolutions and Trotter step data across observables.

The next science task is to test the state-sensitivity layer more systematically:

- add additional motivated states beyond `split_a_ground`;
- test whether the suppression persists at `n_sites=4`;
- refine the second-layer predictor, likely using time-integrated defect response rather than only the initial nested expectation;
- decide whether `electric_density`, `staggered_magnetization`, and `mass_density` need non-product states to reveal their swapped-split leading algebraic sensitivity.

## Bottom Line

Week 5 turns the paper from a binary sensitivity observation into a split- and state-dependent classification result. The most important discovery is that the intermediate class is not empty. `h_hop_density` under the swapped split is the anchor example: algebraically protected at leading order, still capable of visible error for product states, and suppressed for a physically motivated split-ground-state protocol.

That is a stronger and more interesting paper than the original roadmap predicted.
