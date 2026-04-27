from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.sparse import issparse
from scipy.sparse.linalg import eigsh

from z2_trotter import (
    Z2ModelParams,
    Z2ToyModel,
    Z2ToyModelSparse,
    available_splits,
    build_split_terms,
    domain_wall_matter_plus_links_x,
    exact_evolve,
    expectation,
    fit_power_law,
    gauss_sector_signs,
    gauss_violation,
    neel_matter_plus_links_x,
    state_infidelity,
    trotter_evolve,
    uniform_matter_plus_links_x,
)


def parse_float_list(raw: str) -> List[float]:
    values = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one float value.")
    return values


def parse_int_list(raw: str) -> List[int]:
    values = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one int value.")
    return values


def parse_str_list(raw: str) -> List[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one string value.")
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Week-2 scan: multi-time, multi-state, and defect-operator diagnostics."
    )
    parser.add_argument("--n-sites", default="3,4", help="Comma-separated values, e.g. 3,4")
    parser.add_argument("--g-values", default="0.5,1.0,1.5", help="Comma-separated values")
    parser.add_argument(
        "--dts",
        default="0.5,0.25,0.125,0.0625,0.03125",
        help="Comma-separated timestep values",
    )
    parser.add_argument(
        "--t-finals",
        default="0.5,1.0,2.0,4.0",
        help="Comma-separated target final times",
    )
    parser.add_argument("--j", type=float, default=1.0, help="Hopping coefficient")
    parser.add_argument("--m", type=float, default=0.5, help="Staggered mass coefficient")
    parser.add_argument(
        "--backend",
        default="dense",
        choices=["dense", "sparse"],
        help="Matrix backend for model construction and evolution",
    )
    parser.add_argument(
        "--observable",
        default="h_hop_density",
        choices=[
            "h_hop_density",
            "staggered_magnetization",
            "electric_density",
            "mass_density",
            "total_energy_density",
        ],
        help="Observable used for error scaling diagnostics",
    )
    parser.add_argument(
        "--split",
        default="original",
        choices=available_splits(),
        help="Hamiltonian split used by Trotter and defect diagnostics",
    )
    parser.add_argument(
        "--initial-states",
        default="neel_x,uniform_x,domain_wall_x",
        help="Comma-separated initial-state keys",
    )
    parser.add_argument(
        "--strict-time-match",
        action="store_true",
        help="Skip points where rounded step count does not reproduce target time",
    )
    parser.add_argument(
        "--time-match-tol",
        type=float,
        default=1e-12,
        help="Tolerance for strict target-time matching",
    )
    parser.add_argument("--output", default="results/week2_scan.csv", help="Raw CSV output")
    parser.add_argument(
        "--fit-output",
        default="results/week2_fits.csv",
        help="Fit-table CSV output",
    )
    parser.add_argument(
        "--summary",
        default="results/week2_summary.txt",
        help="Summary output path",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress printing the full textual summary to stdout",
    )
    return parser.parse_args()


def build_observable(model, name: str):
    if name == "h_hop_density":
        return model.h_hop / model.n_sites
    if name == "staggered_magnetization":
        return model.staggered_magnetization_operator()
    if name == "electric_density":
        return model.h_electric / model.n_sites
    if name == "mass_density":
        return model.h_mass / model.n_sites
    if name == "total_energy_density":
        return model.h_total / model.n_sites
    raise ValueError(f"Unsupported observable: {name}")


def build_initial_state(model, state_name: str) -> np.ndarray:
    builders: Dict[str, Callable[[Z2ToyModel], np.ndarray]] = {
        "neel_x": neel_matter_plus_links_x,
        "uniform_x": uniform_matter_plus_links_x,
        "domain_wall_x": domain_wall_matter_plus_links_x,
    }
    if state_name not in builders:
        allowed = ", ".join(sorted(builders.keys()))
        raise ValueError(f"Unknown initial state '{state_name}'. Allowed: {allowed}")
    return builders[state_name](model)


def ground_state(operator) -> np.ndarray:
    if issparse(operator):
        if operator.shape[0] <= 512:
            matrix = operator.toarray()
            _, vectors = np.linalg.eigh(matrix)
            return np.asarray(vectors[:, 0])
        _, vectors = eigsh(operator, k=1, which="SA")
        return np.asarray(vectors[:, 0])

    _, vectors = np.linalg.eigh(operator)
    return np.asarray(vectors[:, 0])


def commutator(a, b):
    return a @ b - b @ a


def build_defect_operators(h_a, h_b):
    comm_ab = commutator(h_a, h_b)
    defect1 = 0.5j * comm_ab
    nested_a = commutator(h_a, comm_ab)
    nested_b = commutator(h_b, comm_ab)
    defect2 = -(nested_a + 2.0 * nested_b) / 24.0
    return defect1, defect2


def compute_observable_response(
    state: np.ndarray,
    observable,
    defect,
) -> float:
    # i[D, O] gives instantaneous observable response to adding D into the Hamiltonian.
    response_operator = 1j * commutator(defect, observable)
    return abs(expectation(state, response_operator))


def fit_entry(
    dts: Sequence[float],
    errors: Sequence[float],
) -> Optional[Tuple[float, float, int]]:
    return fit_power_law(dts=dts, errors=errors)


def pearson_log_correlation(
    predictors: Sequence[float],
    errors: Sequence[float],
) -> Optional[Tuple[float, int]]:
    pairs = [(x, y) for x, y in zip(predictors, errors) if x > 0.0 and y > 0.0]
    if len(pairs) < 2:
        return None

    lx = np.log([x for x, _ in pairs])
    ly = np.log([y for _, y in pairs])

    std_x = float(np.std(lx))
    std_y = float(np.std(ly))
    if std_x == 0.0 or std_y == 0.0:
        return None

    corr = float(np.corrcoef(lx, ly)[0, 1])
    return corr, len(pairs)


def main() -> None:
    args = parse_args()
    n_sites_values = parse_int_list(args.n_sites)
    g_values = parse_float_list(args.g_values)
    dt_values = parse_float_list(args.dts)
    t_final_values = parse_float_list(args.t_finals)
    initial_states = parse_str_list(args.initial_states)

    rows: List[Dict[str, float | int | str]] = []
    fit_rows: List[Dict[str, float | int | str]] = []
    summary_lines: List[str] = []

    predictor_data_all: Dict[int, Dict[str, List[float]]] = {
        1: {"predictor": [], "error": []},
        2: {"predictor": [], "error": []},
    }
    predictor_data_by_time: Dict[int, Dict[float, Dict[str, List[float]]]] = {
        1: defaultdict(lambda: {"predictor": [], "error": []}),
        2: defaultdict(lambda: {"predictor": [], "error": []}),
    }

    for n_sites in n_sites_values:
        for g_value in g_values:
            params = Z2ModelParams(n_sites=n_sites, j=args.j, g=g_value, m=args.m)
            if args.backend == "dense":
                model = Z2ToyModel(params)
            else:
                model = Z2ToyModelSparse(params)
            observable = build_observable(model, args.observable)
            gauss_ops = model.gauss_generators()

            h_a, h_b = build_split_terms(model, args.split)
            defect1, defect2 = build_defect_operators(h_a, h_b)

            for state_name in initial_states:
                if state_name == "split_a_ground":
                    psi0 = ground_state(h_a)
                else:
                    psi0 = build_initial_state(model, state_name)
                sector_signs = gauss_sector_signs(psi0, gauss_ops)

                obs_errors_by_key: Dict[Tuple[float, int], List[Tuple[float, float]]] = defaultdict(list)
                state_errors_by_key: Dict[Tuple[float, int], List[Tuple[float, float]]] = defaultdict(list)

                for t_target in t_final_values:
                    for dt in dt_values:
                        n_steps = int(round(t_target / dt))
                        if n_steps < 1:
                            continue

                        t_used = n_steps * dt
                        if args.strict_time_match and abs(t_used - t_target) > args.time_match_tol:
                            continue

                        psi_exact = exact_evolve(model.h_total, psi0, t_used)
                        obs_exact = expectation(psi_exact, observable)
                        gauss_exact = gauss_violation(psi_exact, gauss_ops, sector_signs)

                        defect1_response = compute_observable_response(
                            state=psi_exact,
                            observable=observable,
                            defect=defect1,
                        )
                        defect2_response = compute_observable_response(
                            state=psi_exact,
                            observable=observable,
                            defect=defect2,
                        )

                        defect1_predictor = dt * defect1_response
                        defect2_predictor = (dt**2) * defect2_response

                        rows.append(
                            {
                                "n_sites": n_sites,
                                "backend": args.backend,
                                "split": args.split,
                                "j": args.j,
                                "g": g_value,
                                "m": args.m,
                                "initial_state": state_name,
                                "t_target": t_target,
                                "dt": dt,
                                "n_steps": n_steps,
                                "t_used": t_used,
                                "observable_name": args.observable,
                                "method": "exact",
                                "observable": obs_exact,
                                "observable_error": 0.0,
                                "state_error": 0.0,
                                "state_infidelity": 0.0,
                                "gauss_violation": gauss_exact,
                                "defect1_obs_response": defect1_response,
                                "defect2_obs_response": defect2_response,
                                "defect1_predictor": defect1_predictor,
                                "defect2_predictor": defect2_predictor,
                            }
                        )

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
                            obs_error = abs(obs_trotter - obs_exact)
                            infidelity = state_infidelity(psi_exact, psi_trotter)
                            state_error = infidelity**0.5
                            gauss_err = gauss_violation(psi_trotter, gauss_ops, sector_signs)

                            rows.append(
                                {
                                    "n_sites": n_sites,
                                    "backend": args.backend,
                                    "split": args.split,
                                    "j": args.j,
                                    "g": g_value,
                                    "m": args.m,
                                    "initial_state": state_name,
                                    "t_target": t_target,
                                    "dt": dt,
                                    "n_steps": n_steps,
                                    "t_used": t_used,
                                    "observable_name": args.observable,
                                    "method": f"trotter{order}",
                                    "observable": obs_trotter,
                                    "observable_error": obs_error,
                                    "state_error": state_error,
                                    "state_infidelity": infidelity,
                                    "gauss_violation": gauss_err,
                                    "defect1_obs_response": defect1_response,
                                    "defect2_obs_response": defect2_response,
                                    "defect1_predictor": defect1_predictor,
                                    "defect2_predictor": defect2_predictor,
                                }
                            )

                            obs_errors_by_key[(t_target, order)].append((dt, obs_error))
                            state_errors_by_key[(t_target, order)].append((dt, state_error))

                            predictor = defect1_predictor if order == 1 else defect2_predictor
                            if predictor > 0.0 and obs_error > 0.0:
                                predictor_data_all[order]["predictor"].append(predictor)
                                predictor_data_all[order]["error"].append(obs_error)
                                predictor_data_by_time[order][t_target]["predictor"].append(predictor)
                                predictor_data_by_time[order][t_target]["error"].append(obs_error)

                summary_lines.append(
                    f"n_sites={n_sites}, g={g_value:.6g}, state={state_name}, "
                    f"observable={args.observable}, split={args.split}, backend={args.backend}"
                )

                for t_target in t_final_values:
                    summary_lines.append(f"  t_target={t_target:.6g}")

                    for order in (1, 2):
                        obs_data = obs_errors_by_key[(t_target, order)]
                        obs_fit = fit_entry(
                            dts=[dt for dt, _ in obs_data],
                            errors=[err for _, err in obs_data],
                        )
                        fit_rows.append(
                            {
                                "n_sites": n_sites,
                                "backend": args.backend,
                                "split": args.split,
                                "j": args.j,
                                "g": g_value,
                                "m": args.m,
                                "initial_state": state_name,
                                "t_target": t_target,
                                "observable_name": args.observable,
                                "method": f"trotter{order}",
                                "metric": "observable_error",
                                "slope": "" if obs_fit is None else obs_fit[0],
                                "prefactor": "" if obs_fit is None else obs_fit[1],
                                "points": 0 if obs_fit is None else obs_fit[2],
                            }
                        )
                        if obs_fit is None:
                            summary_lines.append(
                                f"    trotter{order} observable_error: insufficient points"
                            )
                        else:
                            slope, prefactor, points = obs_fit
                            summary_lines.append(
                                f"    trotter{order} observable_error ~= "
                                f"{prefactor:.3e} * dt^{slope:.3f} (points={points})"
                            )

                        state_data = state_errors_by_key[(t_target, order)]
                        state_fit = fit_entry(
                            dts=[dt for dt, _ in state_data],
                            errors=[err for _, err in state_data],
                        )
                        fit_rows.append(
                            {
                                "n_sites": n_sites,
                                "backend": args.backend,
                                "split": args.split,
                                "j": args.j,
                                "g": g_value,
                                "m": args.m,
                                "initial_state": state_name,
                                "t_target": t_target,
                                "observable_name": args.observable,
                                "method": f"trotter{order}",
                                "metric": "state_error",
                                "slope": "" if state_fit is None else state_fit[0],
                                "prefactor": "" if state_fit is None else state_fit[1],
                                "points": 0 if state_fit is None else state_fit[2],
                            }
                        )
                        if state_fit is None:
                            summary_lines.append(
                                f"    trotter{order} state_error: insufficient points"
                            )
                        else:
                            slope, prefactor, points = state_fit
                            summary_lines.append(
                                f"    trotter{order} state_error ~= "
                                f"{prefactor:.3e} * dt^{slope:.3f} (points={points})"
                            )

                    summary_lines.append("")

    summary_lines.append("Global defect-predictor correlations (log-log Pearson)")
    for order in (1, 2):
        corr = pearson_log_correlation(
            predictors=predictor_data_all[order]["predictor"],
            errors=predictor_data_all[order]["error"],
        )
        if corr is None:
            summary_lines.append(f"  trotter{order}: insufficient data")
        else:
            coefficient, points = corr
            summary_lines.append(
                f"  trotter{order}: r={coefficient:.4f} using {points} points"
            )

    summary_lines.append("")
    summary_lines.append("Time-resolved defect-predictor correlations (log-log Pearson)")
    for t_target in sorted(t_final_values):
        summary_lines.append(f"  t_target={t_target:.6g}")
        for order in (1, 2):
            corr = pearson_log_correlation(
                predictors=predictor_data_by_time[order][t_target]["predictor"],
                errors=predictor_data_by_time[order][t_target]["error"],
            )
            if corr is None:
                summary_lines.append(f"    trotter{order}: insufficient data")
            else:
                coefficient, points = corr
                summary_lines.append(
                    f"    trotter{order}: r={coefficient:.4f} using {points} points"
                )
        summary_lines.append("")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "n_sites",
                "backend",
                "split",
                "j",
                "g",
                "m",
                "initial_state",
                "t_target",
                "dt",
                "n_steps",
                "t_used",
                "observable_name",
                "method",
                "observable",
                "observable_error",
                "state_error",
                "state_infidelity",
                "gauss_violation",
                "defect1_obs_response",
                "defect2_obs_response",
                "defect1_predictor",
                "defect2_predictor",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    fit_output_path = Path(args.fit_output)
    fit_output_path.parent.mkdir(parents=True, exist_ok=True)
    with fit_output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "n_sites",
                "backend",
                "split",
                "j",
                "g",
                "m",
                "initial_state",
                "t_target",
                "observable_name",
                "method",
                "metric",
                "slope",
                "prefactor",
                "points",
            ],
        )
        writer.writeheader()
        writer.writerows(fit_rows)

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write(f"Week-2 scan summary ({timestamp})\n\n")
        handle.write("\n".join(summary_lines))
        handle.write("\n")

    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Wrote {len(fit_rows)} fit rows to {fit_output_path}")
    print(f"Wrote summary to {summary_path}")
    if not args.quiet:
        print()
        for line in summary_lines:
            print(line)


if __name__ == "__main__":
    main()
