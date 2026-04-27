from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from z2_trotter import (
    Z2ModelParams,
    Z2ToyModel,
    exact_evolve,
    expectation,
    fit_power_law,
    gauss_sector_signs,
    gauss_violation,
    neel_matter_plus_links_x,
    state_infidelity,
    trotter_evolve,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Week-1 baseline scan for 1+1D Z2 toy model Trotter errors."
    )
    parser.add_argument("--n-sites", default="4", help="Comma-separated values, e.g. 3,4")
    parser.add_argument("--g-values", default="1.0", help="Comma-separated values, e.g. 0.5,1.0,1.5")
    parser.add_argument("--dts", default="0.4,0.2,0.1,0.05", help="Comma-separated timestep values")
    parser.add_argument("--t-final", type=float, default=2.0, help="Target evolution time")
    parser.add_argument("--j", type=float, default=1.0, help="Hopping coefficient")
    parser.add_argument("--m", type=float, default=0.5, help="Staggered mass coefficient")
    parser.add_argument(
        "--observable",
        default="h_hop_density",
        choices=["h_hop_density", "staggered_magnetization", "electric_density"],
        help="Observable used for error scaling diagnostics",
    )
    parser.add_argument("--output", default="results/week1_scan.csv", help="CSV output path")
    parser.add_argument("--summary", default="results/week1_summary.txt", help="Summary output path")
    return parser.parse_args()


def build_observable(model: Z2ToyModel, name: str):
    if name == "h_hop_density":
        return model.h_hop / model.n_sites
    if name == "staggered_magnetization":
        return model.staggered_magnetization_operator()
    if name == "electric_density":
        return model.h_electric / model.n_sites
    raise ValueError(f"Unsupported observable: {name}")


def main() -> None:
    args = parse_args()
    n_sites_values = parse_int_list(args.n_sites)
    g_values = parse_float_list(args.g_values)
    dt_values = parse_float_list(args.dts)

    rows: List[Dict[str, float | int | str]] = []
    summary_lines: List[str] = []

    for n_sites in n_sites_values:
        for g_value in g_values:
            params = Z2ModelParams(n_sites=n_sites, j=args.j, g=g_value, m=args.m)
            model = Z2ToyModel(params)
            psi0 = neel_matter_plus_links_x(model)

            observable = build_observable(model, args.observable)
            gauss_ops = model.gauss_generators()
            sector_signs = gauss_sector_signs(psi0, gauss_ops)

            obs_errors_by_order: Dict[int, List[tuple[float, float]]] = {1: [], 2: []}
            state_errors_by_order: Dict[int, List[tuple[float, float]]] = {1: [], 2: []}

            for dt in dt_values:
                n_steps = int(round(args.t_final / dt))
                if n_steps < 1:
                    continue

                t_used = n_steps * dt

                psi_exact = exact_evolve(model.h_total, psi0, t_used)
                obs_exact = expectation(psi_exact, observable)
                gauss_exact = gauss_violation(psi_exact, gauss_ops, sector_signs)

                rows.append(
                    {
                        "n_sites": n_sites,
                        "j": args.j,
                        "g": g_value,
                        "m": args.m,
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
                    }
                )

                for order in (1, 2):
                    psi_trotter = trotter_evolve(
                        initial_state=psi0,
                        h_a=model.h_a,
                        h_b=model.h_b,
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
                            "j": args.j,
                            "g": g_value,
                            "m": args.m,
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
                        }
                    )
                    obs_errors_by_order[order].append((dt, obs_error))
                    state_errors_by_order[order].append((dt, state_error))

            summary_lines.append(
                f"n_sites={n_sites}, g={g_value:.6g}, m={args.m:.6g}, j={args.j:.6g}, "
                f"observable={args.observable}"
            )
            for order in (1, 2):
                obs_data = obs_errors_by_order[order]
                obs_fit = fit_power_law(
                    dts=[dt for dt, _ in obs_data],
                    errors=[err for _, err in obs_data],
                )
                if obs_fit is None:
                    summary_lines.append(
                        f"  trotter{order} observable_error: insufficient positive-error points"
                    )
                else:
                    slope, prefactor, used = obs_fit
                    summary_lines.append(
                        f"  trotter{order} observable_error ~= "
                        f"{prefactor:.3e} * dt^{slope:.3f} (points={used})"
                    )

                state_data = state_errors_by_order[order]
                state_fit = fit_power_law(
                    dts=[dt for dt, _ in state_data],
                    errors=[err for _, err in state_data],
                )
                if state_fit is None:
                    summary_lines.append(
                        f"  trotter{order} state_error: insufficient positive-error points"
                    )
                else:
                    slope, prefactor, used = state_fit
                    summary_lines.append(
                        f"  trotter{order} state_error ~= "
                        f"{prefactor:.3e} * dt^{slope:.3f} (points={used})"
                    )
            summary_lines.append("")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "n_sites",
                "j",
                "g",
                "m",
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
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write(f"Week-1 scan summary ({timestamp})\n\n")
        handle.write("\n".join(summary_lines))
        handle.write("\n")

    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Wrote summary to {summary_path}")
    print()
    for line in summary_lines:
        print(line)


if __name__ == "__main__":
    main()
