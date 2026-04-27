# Week-3 Progress Report (Execution Started)

Date: 2026-04-23

## Scope completed in this pass

Executed priorities A and part of B from `week3_plan.md`:

- added new observables to the scan stack
- ran full week-2 grid for each new observable
- generated a classification table with slope/prefactor + defect-proxy fields

## Code changes

- `week3_plan.md`: week-3 priorities and immediate execution checklist
- `run_week2_scan.py`:
  - added observables: `mass_density`, `total_energy_density`
  - added `--quiet` to avoid massive console dumps during long scans
- `analyze_week3_observables.py`:
  - builds a cross-observable table from scan/fit CSV artifacts
  - outputs:
    - `results/week3_observable_table.csv`
    - `results/week3_observable_table.md`

## Runs executed

All runs used:

- `n_sites=3,4`
- `g=0.5,1.0,1.5`
- `dt=0.5,0.25,0.125,0.0625,0.03125`
- `t_target=0.5,1.0,2.0,4.0`
- initial states: `neel_x,uniform_x,domain_wall_x`

New observable runs:

- `electric_density`
- `staggered_magnetization`
- `mass_density`
- `total_energy_density`

Reference baseline reused:

- `h_hop_density` from prior week-2 run

## Observable classification table (current draft)

Source: `results/week3_observable_table.md`

- `h_hop_density`: `sensitive`
- `electric_density`: `blind`
- `staggered_magnetization`: `blind`
- `mass_density`: `blind`
- `total_energy_density`: `sensitive`

## Interpretation for paper narrative (B)

Current data supports centering the story on defect sensitivity:

- some observables exhibit clear first-vs-second order visibility (`sensitive`)
- others effectively hide integrator-order differences (`blind`)
- this aligns with the BCH-defect sensitivity framing rather than a single universal observable behavior

## Remaining week-3 priorities

- C: push one modest size step further (requires sparse/Krylov backend; dense cap currently blocks `n_sites=5`)
- D: keep framing conservative:
  - `structured algorithmic systematics in toy Hamiltonian gauge dynamics, with future relevance to continuum extrapolation`

Size-limit check executed:

- attempting `n_sites=5` currently raises:
  - `ValueError: Dense baseline supports dim <= 512. Got dim=1024; reduce n_sites.`
