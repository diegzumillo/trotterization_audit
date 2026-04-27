# Week-4 Sparse/Krylov n=5 Check

Date: 2026-04-23

## What was added

- sparse model backend: `z2_trotter/model_sparse.py`
- Krylov evolution path (`expm_multiply`) for sparse matrices in `z2_trotter/evolution.py`
- scan backend switch in `run_week2_scan.py`:
  - `--backend dense|sparse`

## Validation check

Dense vs sparse consistency was verified at `n_sites=4`:

- exact evolution max state-entry difference: `7.14e-16`
- trotter1 max state-entry difference: `1.76e-16`
- trotter2 max state-entry difference: `3.25e-16`

This confirms numerical agreement to floating-point precision.

## n=5 focused run

Command executed:

```powershell
python run_week2_scan.py --backend sparse --n-sites 5 --g-values 1.0 --dts 0.25,0.125,0.0625,0.03125 --t-finals 1.0,2.0 --initial-states neel_x,uniform_x --observable h_hop_density --output results/week4_n5_hhop_scan.csv --fit-output results/week4_n5_hhop_fits.csv --summary results/week4_n5_hhop_summary.txt --quiet
```

Outputs:

- `results/week4_n5_hhop_scan.csv`
- `results/week4_n5_hhop_fits.csv`
- `results/week4_n5_hhop_summary.txt`

## Key readout

At `n_sites=5`, state-error order separation remains clear:

- `trotter1 state_error` slopes: approximately `0.997` to `1.038`
- `trotter2 state_error` slopes: approximately `2.009` to `2.028`

Observable behavior (`h_hop_density`) remains channel/state/time dependent, while preserving first-vs-second order separation:

- `trotter1 observable_error` slopes: `0.774`, `1.093`, `1.722`, `0.905`
- `trotter2 observable_error` slopes: `1.986`, `1.990`, `1.992`, `2.018`

Defect-predictor correlations were strong in this focused set:

- global: `r(trotter1)=0.8512`, `r(trotter2)=0.9495`

## Conclusion

The sparse/Krylov step successfully removes the `n_sites=5` blocker and preserves the core structural pattern:

- robust integrator-order signal in state space
- observable-dependent visibility consistent with defect-centered interpretation
