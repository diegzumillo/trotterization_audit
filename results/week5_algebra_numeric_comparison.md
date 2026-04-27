# Week-5 Algebra vs Numerical Visibility

Date: 2026-04-25

Reduced-grid protocol: `n_sites=3`, `g=1.0`, states `neel_x,uniform_x`, `t_final={0.5,1.0}`, `dt={0.5,0.25,0.125,0.0625}`.

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

Interpretation:

The three-class algebra is doing useful work, but the reduced product-state numerics show that operator-level sensitivity is not automatically visible in this protocol. This makes the planned second-layer state test essential rather than optional.
