from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np

from run_week2_scan import build_observable, commutator
from z2_trotter import (
    Z2ModelParams,
    Z2ToyModel,
    available_splits,
    build_split_terms,
    domain_wall_matter_plus_links_x,
    expectation,
    neel_matter_plus_links_x,
    split_description,
    uniform_matter_plus_links_x,
)


OBSERVABLES = (
    "h_hop_density",
    "electric_density",
    "staggered_magnetization",
    "mass_density",
    "total_energy_density",
)

STATE_BUILDERS: Dict[str, Callable[[Z2ToyModel], np.ndarray]] = {
    "neel_x": neel_matter_plus_links_x,
    "uniform_x": uniform_matter_plus_links_x,
    "domain_wall_x": domain_wall_matter_plus_links_x,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Algebraic split classifier for week-5 scope expansion."
    )
    parser.add_argument("--n-sites", type=int, default=3)
    parser.add_argument("--j", type=float, default=1.0)
    parser.add_argument("--g", type=float, default=1.0)
    parser.add_argument("--m", type=float, default=0.5)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--output-csv", default="results/week5_split_algebra.csv")
    parser.add_argument("--output-md", default="results/week5_split_algebra.md")
    return parser.parse_args()


def fro_norm(operator) -> float:
    return float(np.linalg.norm(operator))


def classify(comm_ha_norm: float, nested_norm: float, state_max: float, tol: float) -> str:
    if comm_ha_norm > tol:
        return "leading-defect sensitive"
    if nested_norm <= tol:
        return "fully blind"
    if state_max > tol:
        return "algebraically suppressed but state-sensitive"
    return "state-suppressed blind"


def write_markdown(path: Path, rows: List[Dict[str, float | str]]) -> None:
    lines: List[str] = []
    lines.append("# Week-5 Split Algebra Classifier")
    lines.append("")
    lines.append("Date: 2026-04-25")
    lines.append("")
    lines.append(
        "This is the pre-scan algebraic check for the proposed split-dependence story. "
        "It uses dense operators at `n_sites=3`, `j=1`, `g=1`, `m=0.5`; exact zero/nonzero "
        "operator identities should be size-independent for these local sums, but this is still "
        "a numerical algebra check rather than a proof."
    )
    lines.append("")
    lines.append("Splits:")
    lines.append("")
    for split_name in available_splits():
        lines.append(f"- `{split_name}`: {split_description(split_name)}")
    lines.append("")
    lines.append("| split | observable | ||[O,H_A]|| | ||[H_A,[H_B,O]]|| | max product-state expectation | class |")
    lines.append("|---|---|---:|---:|---:|---|")
    for row in rows:
        lines.append(
            f"| `{row['split']}` | `{row['observable']}` | "
            f"{float(row['comm_ha_norm']):.3e} | "
            f"{float(row['nested_norm']):.3e} | "
            f"{float(row['state_expectation_abs_max']):.3e} | "
            f"**{row['class']}** |"
        )
    lines.append("")
    lines.append("Immediate readout:")
    lines.append("")
    for observable in OBSERVABLES:
        classes = [
            f"`{row['split']}`={row['class']}"
            for row in rows
            if row["observable"] == observable
        ]
        lines.append(f"- `{observable}`: " + "; ".join(classes))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    params = Z2ModelParams(n_sites=args.n_sites, j=args.j, g=args.g, m=args.m)
    model = Z2ToyModel(params)
    states = {name: builder(model) for name, builder in STATE_BUILDERS.items()}

    rows: List[Dict[str, float | str]] = []
    for split_name in available_splits():
        h_a, h_b = build_split_terms(model, split_name)
        for observable_name in OBSERVABLES:
            observable = build_observable(model, observable_name)
            comm_ha = commutator(observable, h_a)
            nested = commutator(h_a, commutator(h_b, observable))
            state_expectations = {
                state_name: abs(expectation(state, nested))
                for state_name, state in states.items()
            }
            state_max = max(state_expectations.values())
            rows.append(
                {
                    "split": split_name,
                    "observable": observable_name,
                    "comm_ha_norm": fro_norm(comm_ha),
                    "nested_norm": fro_norm(nested),
                    "state_expectation_abs_max": state_max,
                    "neel_x_expectation_abs": state_expectations["neel_x"],
                    "uniform_x_expectation_abs": state_expectations["uniform_x"],
                    "domain_wall_x_expectation_abs": state_expectations["domain_wall_x"],
                    "class": classify(
                        fro_norm(comm_ha),
                        fro_norm(nested),
                        state_max,
                        args.tol,
                    ),
                }
            )

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(output_md, rows)

    print(f"Wrote {output_csv}")
    print(f"Wrote {output_md}")


if __name__ == "__main__":
    main()
