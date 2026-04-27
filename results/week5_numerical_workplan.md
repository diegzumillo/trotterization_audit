# Week-5 Numerical Workplan

Date: 2026-04-25

Manuscript status: do not edit `template.tex` during this phase. The goal is to build numerical and algebraic evidence as markdown reports first.

## Current Findings

The split-aware algebraic classifier has been implemented and run:

- report: `results/week5_split_algebra.md`
- data: `results/week5_split_algebra.csv`

Algebraic readout:

- The proposed split-dependence story is viable, but the strongest preliminary claim needs refinement.
- `electric_density`, `staggered_magnetization`, and `mass_density` flip from state-suppressed blind under the original split to noncommuting with `H_A` under the swapped split.
- `h_hop_density` does not become fully blind under the swapped split. It has `[O,H_A]=0`, but `[H_A,[H_B,O]]` is nonzero and has nonzero expectation on the tested product states, so it is classified as algebraically suppressed but state-sensitive.
- A focused swapped-split probe for `h_hop_density` confirms this caution numerically:
  - data: `results/week5_probe_swapped_h_hop_density_scan.csv`
  - fits: `results/week5_probe_swapped_h_hop_density_fits.csv`
  - summary: `results/week5_probe_swapped_h_hop_density_summary.txt`
- Focused swapped-split probes for `electric_density`, `staggered_magnetization`, and `mass_density` do not show a clean leading-error flip on the reduced grid. The probe table classifies them as blind by the week-4 numerical rule:
  - report: `results/week5_probe_swapped_table.md`
  - data: `results/week5_probe_swapped_table.csv`

Interpretation:

- The initial brainstormed Step 1 is too coarse as a standalone predictor for the current product-state protocol.
- The stronger procedure should be framed around the actual defect-response expectation, not only the operator commutator `[O,H_A]`.
- The most robust new result so far is a split-dependent change of algebraic layer, with `h_hop_density` providing a concrete non-empty example of the second-layer state-sensitive class.
- Centerpiece framing: physically natural Hamiltonian regroupings move observables between algebraic classes, and numerical visibility tracks the class rather than the observable identity.

Prediction and comparison reports:

- analytic predictions: `results/week5_analytic_predictions.md`
- reduced original-vs-swapped numerical table: `results/week5_probe_original_swapped_table.md`
- algebra versus numerical visibility: `results/week5_algebra_numeric_comparison.md`

## Immediate Numerical Tasks

1. Extend the focused original-vs-swapped comparison scans only if the reduced grid suggests a stable signal. Current reduced-grid artifacts cover:
   - `n_sites=3`
   - `g=1.0`
   - states: `neel_x,uniform_x`
   - `t_final=0.5,1.0`
   - `dt=0.5,0.25,0.125,0.0625`

2. Keep `results/week5_algebra_numeric_comparison.md` as the draft replacement for the old binary Table I.

3. Test non-product or evolved initial states for the second-layer response, starting with `h_hop_density` under the swapped split.
   - First target: the ground state of `H_A` under the swapped split, i.e. the ground state of `H_hop`.
   - This is physically motivated and avoids an arbitrary entangled-state construction.
   - First reduced-grid report: `results/week5_state_sensitivity.md`

4. Optimize or batch the full-grid scan path. A full default dense swapped-split scan for one observable exceeded 120 seconds, so the expanded campaign should either:
   - use smaller staged grids first, or
   - add caching for exact states and Trotter step unitaries before running all split-observable combinations.

## Revised Centerpiece Candidate

The safest centerpiece is not "`h_hop_density` becomes blind under Split II" and not yet "`the blind channels become numerically sensitive under Split II" for the current product-state protocol. The sharper supported claim is:

Physically natural Hamiltonian regroupings move observables between algebraic classes, and numerical visibility tracks the class rather than the observable identity.

## Next Reports To Produce

- `results/week5_full_split_table.md`: full-grid split-dependence map after scan optimization.
