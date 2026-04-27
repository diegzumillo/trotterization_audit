# Week-3 Observable Sensitivity Table

Date: 2026-04-23

Classification rule used in this draft:

- `blind`: `delta_q < 0.4` and median small-`dt` error ratio `< 1.5`
- `sensitive`: `delta_q > 0.7` and median small-`dt` error ratio `> 3.0`
- otherwise `intermediate`

| observable | trotter1 fit (q,c) | trotter2 fit (q,c) | defect proxy (mean response, r) | class |
|---|---:|---:|---:|---|
| `h_hop_density` | q1=1.111, c1=5.756e-01 | q2=2.028, c2=2.528e-01 | <D1>=1.803e+00, <D2>=3.323e-01; r1=0.679, r2=0.824 | **sensitive** |
| `electric_density` | q1=1.946, c1=3.735e-01 | q2=1.946, c2=3.735e-01 | <D1>=1.431e+00, <D2>=1.733e-01; r1=0.763, r2=0.805 | **blind** |
| `staggered_magnetization` | q1=2.037, c1=3.740e-01 | q2=2.037, c2=3.740e-01 | <D1>=1.629e+00, <D2>=2.531e-01; r1=0.831, r2=0.785 | **blind** |
| `mass_density` | q1=2.037, c1=1.870e-01 | q2=2.037, c2=1.870e-01 | <D1>=8.144e-01, <D2>=1.266e-01; r1=0.831, r2=0.785 | **blind** |
| `total_energy_density` | q1=1.209, c1=7.387e-01 | q2=2.093, c2=5.043e-01 | <D1>=1.068e+00, <D2>=5.667e-01; r1=0.562, r2=0.853 | **sensitive** |

Supporting metrics (`delta_q`, median small-`dt` ratio):

- `h_hop_density`: delta_q=0.918, median_ratio_dtmin=43.738
- `electric_density`: delta_q=-0.000, median_ratio_dtmin=1.000
- `staggered_magnetization`: delta_q=0.000, median_ratio_dtmin=1.000
- `mass_density`: delta_q=0.000, median_ratio_dtmin=1.000
- `total_energy_density`: delta_q=0.884, median_ratio_dtmin=36.295
