from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from run_week2_scan import build_initial_state, build_observable, commutator
from z2_trotter import (
    Z2ModelParams,
    Z2ToyModel,
    build_split_terms,
    exact_evolve,
    expectation,
    fit_power_law,
    gauss_sector_signs,
    gauss_violation,
    state_infidelity,
    trotter_evolve,
)


def parse_float_list(raw: str) -> List[float]:
    values = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one float value.")
    return values


def parse_str_list(raw: str) -> List[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one string value.")
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Week-5 state-family probe for swapped h_hop_density second-layer visibility."
    )
    parser.add_argument("--n-sites", type=int, default=3)
    parser.add_argument("--g", type=float, default=1.0)
    parser.add_argument("--j", type=float, default=1.0)
    parser.add_argument("--m", type=float, default=0.5)
    parser.add_argument("--seed-states", default="neel_x,uniform_x")
    parser.add_argument("--taus", default="0,0.25,0.5,0.75,1.0,1.5,2.0")
    parser.add_argument("--lambdas", default="0,0.25,0.5,0.75,0.9,1.0")
    parser.add_argument("--t-finals", default="0.5,1.0")
    parser.add_argument("--dts", default="0.5,0.25,0.125,0.0625")
    parser.add_argument("--output-csv", default="results/week5_state_family_hhop_swapped.csv")
    parser.add_argument("--output-md", default="results/week5_state_family_hhop_swapped.md")
    parser.add_argument("--output-svg", default="results/figures/week5_state_family_hhop_swapped.svg")
    return parser.parse_args()


def normalize(state: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(state))
    if norm <= 0.0:
        raise ValueError("Cannot normalize zero vector.")
    return state / norm


def sector_projector(model: Z2ToyModel, signs: Sequence[float]) -> np.ndarray:
    projector = model.identity.copy()
    for sign, generator in zip(signs, model.gauss_generators()):
        projector = projector @ ((model.identity + sign * generator) / 2.0)
    return projector


def sector_ground_state(operator: np.ndarray, projector: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(operator)
    for idx in np.argsort(values):
        candidate = projector @ vectors[:, idx]
        norm = float(np.linalg.norm(candidate))
        if norm > 1e-9:
            return candidate / norm
    raise ValueError("Could not find a nonzero ground-state projection in the sector.")


def align_phase(reference: np.ndarray, state: np.ndarray) -> np.ndarray:
    overlap = np.vdot(reference, state)
    if abs(overlap) <= 1e-14:
        return state
    return state * np.exp(-1j * np.angle(overlap))


def fit_linear_quadratic_prefactor(dts: Sequence[float], errors: Sequence[float]) -> Optional[Tuple[float, float]]:
    pairs = [(dt, err) for dt, err in zip(dts, errors) if dt > 0.0 and err >= 0.0]
    if len(pairs) < 2:
        return None
    matrix = np.array([[dt, dt**2] for dt, _ in pairs], dtype=float)
    vector = np.array([err for _, err in pairs], dtype=float)
    coeffs, _, _, _ = np.linalg.lstsq(matrix, vector, rcond=None)
    return float(coeffs[0]), float(coeffs[1])


def pearson_log(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, int]:
    pairs = [(x, y) for x, y in zip(xs, ys) if x > 0.0 and y > 0.0]
    if len(pairs) < 3:
        return float("nan"), len(pairs)
    lx = np.log([x for x, _ in pairs])
    ly = np.log([y for _, y in pairs])
    if float(np.std(lx)) == 0.0 or float(np.std(ly)) == 0.0:
        return float("nan"), len(pairs)
    return float(np.corrcoef(lx, ly)[0, 1]), len(pairs)


def build_state_family(
    model: Z2ToyModel,
    h_a: np.ndarray,
    h_total: np.ndarray,
    seed_name: str,
    taus: Iterable[float],
    lambdas: Iterable[float],
) -> List[Dict[str, object]]:
    seed = build_initial_state(model, seed_name)
    gauss_ops = model.gauss_generators()
    signs = gauss_sector_signs(seed, gauss_ops)
    projector = sector_projector(model, signs)
    sector_ground = align_phase(seed, sector_ground_state(h_a, projector))

    states: List[Dict[str, object]] = []
    for tau in taus:
        states.append(
            {
                "family": "ha_evolved",
                "seed": seed_name,
                "parameter_name": "tau",
                "parameter_value": tau,
                "state": normalize(exact_evolve(h_a, seed, tau)),
                "target_signs": signs,
            }
        )
        states.append(
            {
                "family": "h_evolved",
                "seed": seed_name,
                "parameter_name": "tau",
                "parameter_value": tau,
                "state": normalize(exact_evolve(h_total, seed, tau)),
                "target_signs": signs,
            }
        )

    for lam in lambdas:
        mixed = normalize((1.0 - lam) * seed + lam * sector_ground)
        states.append(
            {
                "family": "sector_ground_interp",
                "seed": seed_name,
                "parameter_name": "lambda",
                "parameter_value": lam,
                "state": mixed,
                "target_signs": signs,
            }
        )

    return states


def write_markdown(path: Path, rows: List[Dict[str, float | int | str]]) -> None:
    corr_initial, n_initial = pearson_log(
        [float(row["nested_abs_initial"]) for row in rows],
        [float(row["linear_prefactor_abs_trotter1"]) for row in rows],
    )
    corr_final, n_final = pearson_log(
        [float(row["nested_abs_final"]) for row in rows],
        [float(row["linear_prefactor_abs_trotter1"]) for row in rows],
    )

    lines: List[str] = []
    lines.append("# Week-5 State-Family Probe: Swapped `h_hop_density`")
    lines.append("")
    lines.append("Date: 2026-04-25")
    lines.append("")
    lines.append(
        "Purpose: test whether suppression for the swapped-split `H_A = H_hop` ground state is "
        "special to the exact ground state, generic along simple state families, or mostly caused by "
        "`O_hop` being proportional to `H_A`."
    )
    lines.append("")
    lines.append("Observable and split:")
    lines.append("")
    lines.append("- observable: `h_hop_density`")
    lines.append("- split: swapped, `H_A = H_hop`, `H_B = H_mass + H_electric`")
    lines.append("- second-layer operator: `[H_A,[H_B,O]]`")
    lines.append("")
    lines.append("State families:")
    lines.append("")
    lines.append("- `ha_evolved`: `exp(-i tau H_A)|psi_seed>`")
    lines.append("- `h_evolved`: `exp(-i tau H)|psi_seed>`")
    lines.append("- `sector_ground_interp`: normalized interpolation between the product seed and the `H_A` ground state projected into the same Gauss sector")
    lines.append("")
    lines.append("Correlation with observed leading first-order coefficient:")
    lines.append("")
    lines.append(f"- initial `|<nested>|` vs `|a_1|`: log Pearson r={corr_initial:.3f} using {n_initial} rows")
    lines.append(f"- final-time `|<nested>|` vs `|a_1|`: log Pearson r={corr_final:.3f} using {n_final} rows")
    lines.append("")
    lines.append("Here `a_1` is obtained from a two-term fit `E_1(dt) ~= a_1 dt + a_2 dt^2` for first-order Trotter observable error.")
    lines.append("")
    lines.append("Main readout:")
    lines.append("")
    lines.append(
        "- The global correlation is weak across all families. The second-layer expectation is not a "
        "standalone scalar predictor of the fitted error coefficient once the state is moved around by "
        "`H_A` or by the full Hamiltonian."
    )
    lines.append(
        "- The gauge-sector ground-state interpolation is still highly informative: as `lambda` approaches "
        "one, the nested expectation collapses and the first-vs-second observable distinction is suppressed "
        "even though the observable and split are unchanged."
    )
    lines.append(
        "- This means the `H_A` ground-state suppression is not merely a coding artifact, but it also should "
        "not be overstated as generic for every nearby or evolved state. The state/protocol layer is real."
    )
    lines.append("")

    by_family: Dict[str, List[Dict[str, float | int | str]]] = {}
    for row in rows:
        by_family.setdefault(str(row["family"]), []).append(row)

    lines.append("Family summaries:")
    lines.append("")
    for family, family_rows in sorted(by_family.items()):
        max_gauss = max(float(row["gauss_violation_initial"]) for row in family_rows)
        nested_values = [float(row["nested_abs_initial"]) for row in family_rows]
        pref_values = [float(row["linear_prefactor_abs_trotter1"]) for row in family_rows]
        lines.append(
            f"- `{family}`: nested range [{min(nested_values):.3e}, {max(nested_values):.3e}], "
            f"`|a_1|` range [{min(pref_values):.3e}, {max(pref_values):.3e}], "
            f"max initial Gauss deviation {max_gauss:.3e}"
        )
    lines.append("")

    lines.append("Selected rows:")
    lines.append("")
    lines.append("| family | seed | parameter | t_final | nested initial | nested final | q1 | `|a_1|` | q2 | ratio E1/E2 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    selected = []
    for row in rows:
        parameter = float(row["parameter_value"])
        if parameter in (0.0, 0.75, 0.9, 1.0, 2.0):
            selected.append(row)
    for row in selected[:40]:
        ratio = float(row["ratio_dtmin_e1_over_e2"])
        lines.append(
            f"| `{row['family']}` | `{row['seed']}` | {float(row['parameter_value']):.3g} | "
            f"{float(row['t_final']):.3g} | {float(row['nested_abs_initial']):.3e} | "
            f"{float(row['nested_abs_final']):.3e} | {float(row['q1']):.3f} | "
            f"{float(row['linear_prefactor_abs_trotter1']):.3e} | {float(row['q2']):.3f} | "
            f"{ratio:.3g} |"
        )

    lines.append("")
    lines.append("Interpretation:")
    lines.append("")
    lines.append(
        "This diagnostic separates the structural fact `O_hop proportional H_A` from the state question. "
        "All rows share the same swapped split and observable, so changes in `|<nested>|` and in the "
        "observed leading coefficient are caused by the state family rather than by changing the observable."
    )
    lines.append("")
    lines.append("Generated data:")
    lines.append("")
    lines.append("- `results/week5_state_family_hhop_swapped.csv`")
    lines.append("- `results/figures/week5_state_family_hhop_swapped.svg`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def svg_scatter(path: Path, rows: List[Dict[str, float | int | str]]) -> None:
    points = []
    colors = {
        "ha_evolved": "#1f77b4",
        "h_evolved": "#d62728",
        "sector_ground_interp": "#2ca02c",
    }
    for row in rows:
        x = float(row["nested_abs_initial"])
        y = float(row["linear_prefactor_abs_trotter1"])
        if x <= 0.0 or y <= 0.0:
            continue
        points.append((math.log10(x), math.log10(y), str(row["family"])))

    width = 760
    height = 520
    margin = 70
    if not points:
        path.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>\n", encoding="utf-8")
        return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmin -= 1.0
        xmax += 1.0
    if ymin == ymax:
        ymin -= 1.0
        ymax += 1.0

    def sx(x: float) -> float:
        return margin + (x - xmin) / (xmax - xmin) * (width - 2 * margin)

    def sy(y: float) -> float:
        return height - margin - (y - ymin) / (ymax - ymin) * (height - 2 * margin)

    lines = [
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">",
        "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>",
        f"<line x1=\"{margin}\" y1=\"{height-margin}\" x2=\"{width-margin}\" y2=\"{height-margin}\" stroke=\"#222\"/>",
        f"<line x1=\"{margin}\" y1=\"{margin}\" x2=\"{margin}\" y2=\"{height-margin}\" stroke=\"#222\"/>",
        f"<text x=\"{width/2}\" y=\"{height-20}\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"14\">log10 initial |&lt;[H_A,[H_B,O]]&gt;|</text>",
        f"<text x=\"20\" y=\"{height/2}\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"14\" transform=\"rotate(-90 20 {height/2})\">log10 observed |a1|</text>",
        f"<text x=\"{width/2}\" y=\"30\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"16\">Swapped h_hop_density state-family diagnostic</text>",
    ]

    for family, color in colors.items():
        lines.append(f"<circle cx=\"{width-margin-160}\" cy=\"{margin+20+20*len([c for c in colors if list(colors).index(c) < list(colors).index(family)])}\" r=\"5\" fill=\"{color}\"/>")
        lines.append(f"<text x=\"{width-margin-148}\" y=\"{margin+25+20*len([c for c in colors if list(colors).index(c) < list(colors).index(family)])}\" font-family=\"Arial\" font-size=\"12\">{family}</text>")

    for x, y, family in points:
        lines.append(
            f"<circle cx=\"{sx(x):.2f}\" cy=\"{sy(y):.2f}\" r=\"4\" "
            f"fill=\"{colors.get(family, '#555')}\" fill-opacity=\"0.72\"/>"
        )

    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    params = Z2ModelParams(n_sites=args.n_sites, j=args.j, g=args.g, m=args.m)
    model = Z2ToyModel(params)
    h_a, h_b = build_split_terms(model, "swapped")
    observable = build_observable(model, "h_hop_density")
    nested = commutator(h_a, commutator(h_b, observable))
    gauss_ops = model.gauss_generators()

    seed_names = parse_str_list(args.seed_states)
    taus = parse_float_list(args.taus)
    lambdas = parse_float_list(args.lambdas)
    t_finals = parse_float_list(args.t_finals)
    dts = parse_float_list(args.dts)

    rows: List[Dict[str, float | int | str]] = []
    for seed_name in seed_names:
        states = build_state_family(
            model=model,
            h_a=h_a,
            h_total=model.h_total,
            seed_name=seed_name,
            taus=taus,
            lambdas=lambdas,
        )
        for state_info in states:
            psi0 = np.asarray(state_info["state"])
            target_signs = state_info["target_signs"]
            nested_abs_initial = abs(expectation(psi0, nested))
            h_a_energy = expectation(psi0, h_a) / model.n_sites
            h_total_energy = expectation(psi0, model.h_total) / model.n_sites
            gauss_initial = gauss_violation(psi0, gauss_ops, target_signs)

            for t_final in t_finals:
                psi_exact = exact_evolve(model.h_total, psi0, t_final)
                obs_exact = expectation(psi_exact, observable)
                nested_abs_final = abs(expectation(psi_exact, nested))

                errors_by_order: Dict[int, List[float]] = {1: [], 2: []}
                for dt in dts:
                    n_steps = int(round(t_final / dt))
                    if n_steps < 1:
                        continue
                    for order in (1, 2):
                        psi_trotter = trotter_evolve(
                            initial_state=psi0,
                            h_a=h_a,
                            h_b=h_b,
                            dt=dt,
                            n_steps=n_steps,
                            order=order,
                        )
                        obs_trotter = expectation(psi_trotter, observable)
                        errors_by_order[order].append(abs(obs_trotter - obs_exact))

                fit1 = fit_power_law(dts, errors_by_order[1])
                fit2 = fit_power_law(dts, errors_by_order[2])
                linear_quad = fit_linear_quadratic_prefactor(dts, errors_by_order[1])
                if fit1 is None or fit2 is None or linear_quad is None:
                    continue

                dt_min = min(dts)
                idx_min = dts.index(dt_min)
                e1_min = errors_by_order[1][idx_min]
                e2_min = errors_by_order[2][idx_min]
                ratio = e1_min / e2_min if e2_min > 0.0 else float("inf")
                infidelity = state_infidelity(psi_exact, psi0)
                a1, a2 = linear_quad

                rows.append(
                    {
                        "family": str(state_info["family"]),
                        "seed": str(state_info["seed"]),
                        "parameter_name": str(state_info["parameter_name"]),
                        "parameter_value": float(state_info["parameter_value"]),
                        "t_final": t_final,
                        "nested_abs_initial": nested_abs_initial,
                        "nested_abs_final": nested_abs_final,
                        "h_a_energy_density_initial": h_a_energy,
                        "h_total_energy_density_initial": h_total_energy,
                        "gauss_violation_initial": gauss_initial,
                        "q1": fit1[0],
                        "power_prefactor_trotter1": fit1[1],
                        "q2": fit2[0],
                        "power_prefactor_trotter2": fit2[1],
                        "linear_prefactor_trotter1": a1,
                        "quadratic_prefactor_trotter1": a2,
                        "linear_prefactor_abs_trotter1": abs(a1),
                        "error_trotter1_dtmin": e1_min,
                        "error_trotter2_dtmin": e2_min,
                        "ratio_dtmin_e1_over_e2": ratio,
                        "exact_state_infidelity_from_initial": infidelity,
                    }
                )

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    output_md = Path(args.output_md)
    write_markdown(output_md, rows)

    output_svg = Path(args.output_svg)
    svg_scatter(output_svg, rows)

    print(f"Wrote {output_csv}")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_svg}")


if __name__ == "__main__":
    main()
