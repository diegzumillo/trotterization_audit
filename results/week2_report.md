# Week-2 Results Report

Date: 2026-04-23

## Scope and run configuration

This run executed the week-2 workflow requested in `week2_plan.md`:

- multi-time scan: `t_target = {0.5, 1.0, 2.0, 4.0}`
- sizes: `n_sites = {3, 4}`
- couplings: `g = {0.5, 1.0, 1.5}` with `m=0.5`, `j=1.0`
- timesteps: `dt = {0.5, 0.25, 0.125, 0.0625, 0.03125}`
- initial states: `neel_x`, `uniform_x`, `domain_wall_x`
- observable: `h_hop_density`

Generated artifacts:

- raw rows: `results/week2_scan.csv`
- fit table (exponent + prefactor): `results/week2_fits.csv`
- full textual dump: `results/week2_summary.txt`

## Step 1: Multi-time scan outcome

State-error scaling stayed structurally stable over time:

- `trotter1 state_error` slope mean by time:
  - `t=0.5`: `1.028`
  - `t=1.0`: `1.031`
  - `t=2.0`: `1.057`
  - `t=4.0`: `1.082`
- `trotter2 state_error` slope mean by time:
  - `t=0.5`: `2.054`
  - `t=1.0`: `2.039`
  - `t=2.0`: `2.048`
  - `t=4.0`: `2.049`

Interpretation:

- the integrator-order signal is robust over time in state space;
- no evidence that the order signal is only transient.

For the chosen observable (`h_hop_density`), behavior is structured but more variable:

- `trotter1 observable` slope means by time: `1.162`, `1.065`, `0.954`, `1.262`
- `trotter2 observable` slope means by time: `1.985`, `2.088`, `1.939`, `2.102`

Interpretation:

- observable-level oddities are real and time-dependent, not pure one-time artifacts.

## Step 2: Leading coefficients (prefactors)

Prefactors are strongly channel-dependent.

Examples (mean prefactor across states/couplings/sizes):

- `trotter1 observable_error` prefactor:
  - `t=1.0`: `2.936e-01`
  - `t=4.0`: `6.669e-01`
- `trotter2 observable_error` prefactor:
  - `t=0.5`: `1.259e-01`
  - `t=4.0`: `3.576e-01`

State-error prefactors also increase with time:

- `trotter2 state_error` mean prefactor rises from `5.878e-01` (`t=0.5`) to `1.352e+00` (`t=4.0`).

Interpretation:

- exponent-only statements miss important structure;
- amplitude carries meaningful observable/time dependence.

## Step 3: Defect-operator diagnostics (BCH)

Implemented defect operators:

- first order:
  - `D1 = (i/2)[H_A, H_B]`, with `H_eff = H + dt*D1 + O(dt^2)`
- second order:
  - `D2 = -(1/24)([H_A,[H_A,H_B]] + 2[H_B,[H_A,H_B]])`, with `H_eff = H + dt^2*D2 + O(dt^4)`

Used sensitivity proxies:

- `|<psi| i[D1,O] |psi>|`
- `|<psi| i[D2,O] |psi>|`

Log-log correlations between observable error and defect-based predictors:

- global:
  - `trotter1`: `r = 0.6794` (360 points)
  - `trotter2`: `r = 0.8242` (360 points)
- by time:
  - `t=0.5`: `r1=0.8930`, `r2=0.8400`
  - `t=1.0`: `r1=0.8021`, `r2=0.7712`
  - `t=2.0`: `r1=0.5593`, `r2=0.9172`
  - `t=4.0`: `r1=0.7834`, `r2=0.8931`

Interpretation:

- defect-operator proxies track observable-error structure nontrivially, especially for `trotter2`.

## Step 4: Initial-state robustness

State robustness is strong for state-error exponents and weaker for observable exponents.

Std across initial states (aggregated over size/coupling/time):

- `trotter1 state_error` slope std mean: `0.018`
- `trotter2 state_error` slope std mean: `0.009`
- `trotter1 observable_error` slope std mean: `0.232`
- `trotter2 observable_error` slope std mean: `0.220`

Interpretation:

- order signatures are robust at state level;
- observable-level sensitivity is genuinely state-dependent, matching the proposed paper angle.

## Step 5: Larger systems (current status)

This run includes `n_sites=3,4`. The core pattern (order separation in state error) persists in both.

Finite-size note:

- some observable channels show broad slope variation at fixed time,
- so larger-size extension remains important before strong universality claims.

## Additional diagnostics

Gauge-sector stability remained excellent:

- mean `|gauss_violation|`:
  - exact: `6.79e-16`
  - trotter1: `1.64e-15`
  - trotter2: `1.78e-15`

No gauge drift signal beyond numerical noise was detected in this setup.

## Verdict vs updated research target

This data supports the updated short-term target:

`Trotter defects have structured, observable-dependent signatures in toy Hamiltonian lattice gauge theory, with strong channel dependence in visibility of integrator order.`

The stronger continuum-systematics statement is still plausible, but should wait for:

- larger-size extension and/or sparse-Krylov runs,
- multi-observable defect matching beyond a single default observable,
- and tighter control of pre-asymptotic regions.
