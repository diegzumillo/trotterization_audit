# Week-4 Sensitivity Map

Date: 2026-04-23

Canonical table built from week-2/week-3 scan artifacts over `n_sites={3,4}`, `g={0.5,1.0,1.5}`, `t_target={0.5,1.0,2.0,4.0}`, `dt={0.5,0.25,0.125,0.0625,0.03125}`, and states `neel_x, uniform_x, domain_wall_x`.

Class thresholds used:

- `blind`: `delta_q_mean < 0.4` and median small-`dt` ratio `< 1.5`
- `sensitive`: `delta_q_mean > 0.7` and median small-`dt` ratio `> 3.0`
- otherwise `intermediate`

| observable | slopes `(q1,q2)` mean[min,max] | prefactors `(c1,c2)` mean[min,max] | defect proxy + corr | class |
|---|---:|---:|---:|---|
| `h_hop_density` | q1=1.111[0.229,2.464], q2=2.028[0.703,3.574] | c1=5.756e-01[1.679e-02,1.393e+00], c2=2.528e-01[1.211e-03,1.063e+00] | <D1>=1.803e+00, <D2>=3.323e-01, r1=0.679, r2=0.824, ratio_dtmin=43.738 | **sensitive** |
| `electric_density` | q1=1.946[0.493,2.554], q2=1.946[0.493,2.554] | c1=3.735e-01[9.544e-04,1.494e+00], c2=3.735e-01[9.544e-04,1.494e+00] | <D1>=1.431e+00, <D2>=1.733e-01, r1=0.763, r2=0.805, ratio_dtmin=1.000 | **blind** |
| `staggered_magnetization` | q1=2.037[1.341,2.388], q2=2.037[1.341,2.388] | c1=3.740e-01[5.992e-03,1.481e+00], c2=3.740e-01[5.992e-03,1.481e+00] | <D1>=1.629e+00, <D2>=2.531e-01, r1=0.831, r2=0.785, ratio_dtmin=1.000 | **blind** |
| `mass_density` | q1=2.037[1.341,2.388], q2=2.037[1.341,2.388] | c1=1.870e-01[2.996e-03,7.405e-01], c2=1.870e-01[2.996e-03,7.405e-01] | <D1>=8.144e-01, <D2>=1.266e-01, r1=0.831, r2=0.785, ratio_dtmin=1.000 | **blind** |
| `total_energy_density` | q1=1.209[-0.376,2.410], q2=2.093[1.860,2.289] | c1=7.387e-01[2.843e-03,2.478e+00], c2=5.043e-01[7.961e-02,1.623e+00] | <D1>=1.068e+00, <D2>=5.667e-01, r1=0.562, r2=0.853, ratio_dtmin=36.295 | **sensitive** |
