# Week-5 Split-Dependence Table

Date: 2026-04-25

This report compares the same observable-error diagnostics across Hamiltonian splits.

Splits:

- `original`: H_A = H_mass + H_electric; H_B = H_hop
- `swapped`: H_A = H_hop; H_B = H_mass + H_electric

| observable | original | swapped |
|---|---:|---:|
| `h_hop_density` | **sensitive**; dq=1.214; ratio=113 | **sensitive**; dq=1.443; ratio=21.2 |
| `electric_density` | **blind**; dq=-0.000; ratio=1 | **blind**; dq=-0.060; ratio=0.687 |
| `staggered_magnetization` | **blind**; dq=-0.000; ratio=1 | **blind**; dq=-0.046; ratio=0.884 |
| `mass_density` | **blind**; dq=-0.000; ratio=1 | **blind**; dq=-0.046; ratio=0.884 |
| `total_energy_density` | **sensitive**; dq=0.749; ratio=12.3 | **sensitive**; dq=0.781; ratio=9.85 |

Headline flips:

