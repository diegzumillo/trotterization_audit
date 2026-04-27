from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

from build_week4_sensitivity_map import compute_row
from z2_trotter import split_description


OBSERVABLES = (
    "h_hop_density",
    "electric_density",
    "staggered_magnetization",
    "mass_density",
    "total_energy_density",
)

SPLITS = (
    "original",
    "swapped",
    "electric_isolated",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build week-5 split-dependence table from scan/fit CSV artifacts."
    )
    parser.add_argument("--results-dir", default="results", help="Directory with CSV artifacts")
    parser.add_argument(
        "--splits",
        default=",".join(SPLITS),
        help="Comma-separated split names to include",
    )
    parser.add_argument(
        "--observables",
        default=",".join(OBSERVABLES),
        help="Comma-separated observable names to include",
    )
    parser.add_argument(
        "--output-csv",
        default="week5_split_table.csv",
        help="Output CSV filename inside results dir",
    )
    parser.add_argument(
        "--output-md",
        default="week5_split_table.md",
        help="Output markdown filename inside results dir",
    )
    parser.add_argument(
        "--artifact-prefix",
        default="week5",
        help="Filename prefix for non-original split artifacts",
    )
    return parser.parse_args()


def parse_list(raw: str) -> List[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one value.")
    return values


def artifact_names(split_name: str, observable: str, artifact_prefix: str) -> Tuple[str, str]:
    if split_name == "original":
        if artifact_prefix != "week5":
            prefix = f"{artifact_prefix}_{split_name}_{observable}"
            return f"{prefix}_scan.csv", f"{prefix}_fits.csv"
        if observable == "h_hop_density":
            return "week2_scan.csv", "week2_fits.csv"
        suffix = {
            "electric_density": "electric",
            "staggered_magnetization": "staggered",
            "mass_density": "mass",
            "total_energy_density": "total_energy",
        }[observable]
        return f"week3_{suffix}_scan.csv", f"week3_{suffix}_fits.csv"

    prefix = f"{artifact_prefix}_{split_name}_{observable}"
    return f"{prefix}_scan.csv", f"{prefix}_fits.csv"


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_markdown(
    path: Path,
    rows: List[Dict[str, float | int | str]],
    split_names: List[str],
) -> None:
    lines: List[str] = []
    lines.append("# Week-5 Split-Dependence Table")
    lines.append("")
    lines.append("Date: 2026-04-25")
    lines.append("")
    lines.append("This report compares the same observable-error diagnostics across Hamiltonian splits.")
    lines.append("")
    lines.append("Splits:")
    lines.append("")
    for split_name in sorted({str(row["split"]) for row in rows}):
        lines.append(f"- `{split_name}`: {split_description(split_name)}")
    lines.append("")
    lines.append("| observable | " + " | ".join(split_names) + " |")
    lines.append("|---|" + "---:|" * len(split_names))

    by_key: Dict[Tuple[str, str], Dict[str, float | int | str]] = {
        (str(row["observable"]), str(row["split"])): row for row in rows
    }
    observables = []
    for row in rows:
        observable = str(row["observable"])
        if observable not in observables:
            observables.append(observable)

    for observable in observables:
        cells = []
        for split_name in split_names:
            row = by_key.get((observable, split_name))
            if row is None:
                cells.append("(missing)")
                continue
            cells.append(
                f"**{row['class']}**; "
                f"dq={float(row['delta_q_mean']):.3f}; "
                f"ratio={float(row['ratio_small_dt_median_e1_over_e2']):.3g}"
            )
        lines.append(f"| `{observable}` | {' | '.join(cells)} |")

    lines.append("")
    lines.append("Headline flips:")
    lines.append("")
    for observable in observables:
        original = by_key.get((observable, "original"))
        if original is None:
            continue
        original_class = str(original["class"])
        flips = []
        for split_name in split_names:
            row = by_key.get((observable, split_name))
            if row is not None and str(row["class"]) != original_class:
                flips.append(f"`{split_name}` -> **{row['class']}**")
        if flips:
            lines.append(f"- `{observable}`: original **{original_class}**, " + ", ".join(flips))

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    results_dir = Path(args.results_dir)
    split_names = parse_list(args.splits)
    observable_names = parse_list(args.observables)

    rows: List[Dict[str, float | int | str]] = []
    missing: List[str] = []
    for split_name in split_names:
        for observable in observable_names:
            scan_name, fit_name = artifact_names(split_name, observable, args.artifact_prefix)
            scan_path = results_dir / scan_name
            fit_path = results_dir / fit_name
            if not scan_path.exists() or not fit_path.exists():
                missing.append(f"{split_name}/{observable}: {scan_name}, {fit_name}")
                continue
            row = compute_row(observable, read_csv(scan_path), read_csv(fit_path))
            row["split"] = split_name
            rows.append(row)

    if not rows:
        details = "\n".join(missing)
        raise FileNotFoundError(f"No split table inputs found.\n{details}")

    output_csv = results_dir / args.output_csv
    fieldnames = list(rows[0].keys())
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    output_md = results_dir / args.output_md
    write_markdown(output_md, rows, split_names)

    print(f"Wrote {output_csv}")
    print(f"Wrote {output_md}")
    if missing:
        print("Missing inputs:")
        for item in missing:
            print(f"  {item}")


if __name__ == "__main__":
    main()
