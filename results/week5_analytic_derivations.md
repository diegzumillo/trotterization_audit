# Week-5 Analytic Split Derivations

Date: 2026-04-25

This note records the simple operator-level derivations behind the split-dependence table. It is separate from the numerical reports.

## Setup

Use the periodic `Z2` toy Hamiltonian

```text
H = H_mass + H_electric + H_hop
H_mass     = m sum_x (-1)^x Z_x
H_electric = g sum_x X_l
H_hop      = -j sum_x X_x Z_l X_{x+1}
```

where matter sites carry Pauli operators `X_x, Z_x`, links carry `X_l, Z_l`, and Pauli operators on different qubits commute. On the same qubit,

```text
[Z, X] != 0, [X, Z] != 0, [X, X] = [Z, Z] = 0.
```

The observables are

```text
O_hop   = H_hop / n
O_elec  = H_electric / n
O_stag  = (1/n) sum_x (-1)^x Z_x
O_mass  = H_mass / n
O_total = H / n
```

The algebraic classifier used here is:

1. If `[O,H_A] != 0`, classify as leading-defect sensitive.
2. If `[O,H_A] = 0` but `[H_A,[H_B,O]] != 0`, classify as second-layer state-sensitive unless the chosen state suppresses its expectation.
3. If both vanish, classify as fully blind at this algebraic order.

## Split I: Original

```text
H_A = H_mass + H_electric
H_B = H_hop
```

### `O_hop`

`O_hop` is proportional to `H_hop`. Since `H_hop` contains matter `X_x` and link `Z_l`, it fails to commute with both:

```text
[H_hop, H_mass] != 0
[H_hop, H_electric] != 0
```

Therefore

```text
[O_hop, H_A] != 0
```

Prediction: leading-defect sensitive.

### `O_elec`

`O_elec` is proportional to `H_electric`, so it commutes with `H_electric`. It also commutes with `H_mass`, since link `X_l` and matter `Z_x` act on different qubits:

```text
[O_elec, H_A] = 0.
```

But `O_elec` does not commute with `H_hop`, because `X_l` anticommutes with the link `Z_l` inside the hopping term:

```text
[H_B, O_elec] = [H_hop, O_elec] != 0.
```

Commuting this with `H_A` gives a nonzero operator in the dense check, but the product states used in the reduced protocol suppress the relevant expectation.

Prediction: state-suppressed blind for the product-state protocol.

### `O_stag` and `O_mass`

`O_stag` is proportional to the same matter `Z_x` structure as `H_mass`, and `O_mass = H_mass/n`. Both commute with `H_mass`, and both commute with `H_electric` because matter and link operators act on different qubits:

```text
[O_stag, H_A] = 0
[O_mass, H_A] = 0.
```

They do not commute with `H_hop`, because matter `Z_x` anticommutes with the matter `X_x` factors in the hopping term. As with `O_elec`, the second-layer operator is nonzero, but the tested product states suppress its expectation.

Prediction: state-suppressed blind for the product-state protocol.

### `O_total`

Since `O_total = (H_A + H_B)/n`,

```text
[O_total, H_A] = [H_B, H_A]/n,
```

which is nonzero whenever the split pieces do not commute.

Prediction: leading-defect sensitive.

## Split II: Swapped

```text
H_A = H_hop
H_B = H_mass + H_electric
```

### `O_hop`

`O_hop` is proportional to `H_hop`, now equal to `H_A`, so

```text
[O_hop, H_A] = 0.
```

However, `H_B` contains both terms that fail to commute with `O_hop`:

```text
[H_mass, O_hop] != 0
[H_electric, O_hop] != 0.
```

The second-layer operator is therefore generically nonzero:

```text
[H_A, [H_B, O_hop]] != 0.
```

Prediction: second-layer state-sensitive, not fully blind.

This is the important refinement relative to the original roadmap. The hopping observable does not simply flip from sensitive to blind; it moves from the leading-sensitive class into the intermediate class.

### `O_elec`

`O_elec` is proportional to `H_electric`. Since `H_A = H_hop`, and hopping terms contain link `Z_l`, while `O_elec` contains link `X_l`,

```text
[O_elec, H_A] = [O_elec, H_hop] != 0.
```

Prediction: leading-defect sensitive at the operator level.

### `O_stag` and `O_mass`

Both are built from matter `Z_x`. Since `H_A = H_hop` contains matter `X_x`,

```text
[O_stag, H_A] != 0
[O_mass, H_A] != 0.
```

Prediction: leading-defect sensitive at the operator level.

### `O_total`

Again,

```text
[O_total, H_A] = [H_B, H_A]/n,
```

which is nonzero.

Prediction: leading-defect sensitive.

## Prediction Table

| observable | Split I class | Split II class | change? |
|---|---|---|---|
| `h_hop_density` | leading-defect sensitive | second-layer state-sensitive | yes |
| `electric_density` | state-suppressed blind | leading-defect sensitive | yes |
| `staggered_magnetization` | state-suppressed blind | leading-defect sensitive | yes |
| `mass_density` | state-suppressed blind | leading-defect sensitive | yes |
| `total_energy_density` | leading-defect sensitive | leading-defect sensitive | no |

## Takeaway

The analytic work supports the revised scope: natural Hamiltonian regroupings move observables between algebraic classes. The most interesting case is `h_hop_density`, because Split II places it in the intermediate class rather than in either binary endpoint.
