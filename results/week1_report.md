# Week-1 Trotterization Results Report

Date: 2026-04-23

## Scope

This report summarizes baseline runs of the 1+1D toy `Z2` workflow implemented in `run_week1_scan.py`.

Parameter grid used:

- `n_sites = {3, 4}`
- `g = {0.5, 1.0, 1.5}`
- `m = 0.5`, `j = 1.0`
- `dt = {0.4, 0.2, 0.1, 0.05, 0.025}`
- `t_final = 2.0`

Methods compared:

- exact evolution
- first-order Lie-Trotter (`trotter1`)
- second-order Suzuki-Trotter (`trotter2`)

Observables scanned:

- `h_hop_density` (main)
- `electric_density` (cross-check)
- `staggered_magnetization` (cross-check)

## Commands Executed

```powershell
python run_week1_scan.py --n-sites 3,4 --g-values 0.5,1.0,1.5 --dts 0.4,0.2,0.1,0.05,0.025 --t-final 2.0 --output results/week1_hhop_scan.csv --summary results/week1_hhop_summary.txt
python run_week1_scan.py --n-sites 3,4 --g-values 0.5,1.0,1.5 --dts 0.4,0.2,0.1,0.05,0.025 --t-final 2.0 --observable electric_density --output results/week1_electric_scan.csv --summary results/week1_electric_summary.txt
python run_week1_scan.py --n-sites 3,4 --g-values 0.5,1.0,1.5 --dts 0.4,0.2,0.1,0.05,0.025 --t-final 2.0 --observable staggered_magnetization --output results/week1_staggered_scan.csv --summary results/week1_staggered_summary.txt
```

## Primary Findings

### 1) State error shows clean order separation

Across all settings (all observables), fitted state-error exponents were:

- `trotter1`: mean `1.053`, range `[1.034, 1.075]`
- `trotter2`: mean `2.035`, range `[2.009, 2.053]`

Interpretation: the integrator order is clearly visible in state-level error scaling.

### 2) Main observable (`h_hop_density`) is informative but not perfectly asymptotic everywhere

For `h_hop_density`, fitted observable-error exponents were:

- `trotter1`: mean `0.937`, range `[0.830, 1.055]`
- `trotter2`: mean `1.812`, range `[1.301, 1.975]`

Interpretation: strong separation between first- and second-order behavior remains visible, though some settings are pre-asymptotic at coarse `dt`.

### 3) Practical gain from second-order Trotter increases at smaller `dt`

For `h_hop_density`, ratio `(trotter1 observable error) / (trotter2 observable error)`:

- `dt=0.20`: mean `2.72` (range `0.53` to `5.96`)
- `dt=0.10`: mean `6.63` (range `3.11` to `10.89`)
- `dt=0.05`: mean `14.11` (range `7.44` to `20.38`)
- `dt=0.025`: mean `28.90` (range `15.88` to `39.18`)

Interpretation: second-order splitting gives increasingly large error reduction in the smaller-step regime.

### 4) Gauge-sector diagnostic is clean in this baseline

Mean absolute Gauss-violation values were at floating-point noise level:

- exact: `4.72e-16` (max `1.25e-15`)
- trotter1: `2.38e-15` (max `1.13e-14`)
- trotter2: `2.23e-15` (max `1.21e-14`)

Interpretation: no meaningful gauge drift in this toy setup under the chosen initialization and decomposition.

## Cross-Observable Notes

For both `electric_density` and `staggered_magnetization`, observable-error exponents for `trotter1` and `trotter2` were nearly identical (around 1.9-2.0). State-error exponents still separated as expected (order ~1 vs ~2).

Interpretation: these observables are not good discriminators of Trotter order in this setup, even though the state-level dynamics clearly are.

## Caveats

- Very small systems only (`n_sites <= 4`), dense linear algebra.
- Single final time (`t_final=2.0`) used here.
- Some `h_hop_density` curves are not monotonic at coarse `dt` before entering asymptotic scaling.
- No continuum-trajectory (`a -> 0`) mapping yet; this is a controlled algorithmic baseline.

## Conclusion vs Project Viability

The week-1 baseline passes the most important early test: Trotter errors are structured and fit stable scaling laws at the state level, with clear first- vs second-order separation. The project should continue to a next stage focused on:

- longer-time windows and multi-time fitting,
- larger systems/sparse-Krylov evolution,
- and finally a controlled continuum-oriented trajectory.
