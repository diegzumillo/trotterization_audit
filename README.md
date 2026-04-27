# Trotterization Week-1 Starter

This repository now contains a minimal, runnable toy experiment for:

- 1+1D `Z2` Hamiltonian lattice gauge dynamics on very small systems
- exact real-time evolution vs first-order and second-order Trotter
- basic scaling diagnostics in timestep `dt`

## What is implemented

- Dense-matrix toy `Z2` model (`z2_trotter/model.py`)
- Initial state helpers (`z2_trotter/states.py`)
- Exact and Trotter evolution (`z2_trotter/evolution.py`)
- Observable and error metrics (`z2_trotter/metrics.py`)
- One command-line scan script (`run_week1_scan.py`)

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_week1_scan.py --n-sites 4 --g-values 1.0 --dts 0.4,0.2,0.1,0.05 --t-final 2.0
```

Outputs:

- `results/week1_scan.csv`
- `results/week1_summary.txt`

The default initial condition is a gauge-sector product state:

- matter in a Neel `Z` pattern
- links in `X+`

The default observable is `h_hop_density`. You can switch with:

```powershell
python run_week1_scan.py --observable staggered_magnetization
python run_week1_scan.py --observable electric_density
```

## Notes

- This is a dense linear algebra baseline intended for small sizes (`n_sites <= 4`).
- It is designed to establish the first signal quickly before moving to larger-scale sparse/Krylov workflows.
