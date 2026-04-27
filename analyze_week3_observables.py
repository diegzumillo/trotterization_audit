from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from statistics import mean, median
from typing import Dict, List, Sequence, Tuple

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build week-3 observable sensitivity table from scan/fit CSV files."
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory containing scan and fit CSV artifacts",
    )
    parser.add_argument(
        "--observables",
        default=(
            "h_hop_density:week2_scan.csv:week2_fits.csv,"
            "electric_density:week3_electric_scan.csv:week3_electric_fits.csv,"
            "staggered_magnetization:week3_staggered_scan.csv:week3_staggered_fits.csv,"
            "mass_density:week3_mass_scan.csv:week3_mass_fits.csv,"
            "total_energy_density:week3_total_energy_scan.csv:week3_total_energy_fits.csv"
        ),
        help="Comma-separated entries: observable:scan_csv:fit_csv",
    )
    parser.add_argument(
        "--output-csv",
        default="week3_observable_table.csv",
        help="Output CSV filename inside results directory",
    )
    parser.add_argument(
        "--output-md",
        default="week3_observable_table.md",
        help="Output markdown filename inside results directory",
    )
    return parser.parse_args()


def parse_observable_specs(raw: str) -> List[Tuple[str, str, str]]:
    specs: List[Tuple[str, str, str]] = []
    for part in raw.split(","):
        item = part.strip()
        if not item:
            continue
        chunks = item.split(":")
        if len(chunks) != 3:
            raise ValueError(
                f"Invalid observable spec '{item}'. Expected observable:scan.csv:fit.csv"
            )
        specs.append((chunks[0], chunks[1], chunks[2]))
    if not specs:
        raise ValueError("At least one observable spec is required.")
    return specs


def pearson_log_correlation(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, int]:
    pairs = [(x, y) for x, y in zip(xs, ys) if x > 0.0 and y > 0.0]
    if len(pairs) < 2:
        return float("nan"), 0

    lx = np.log([x for x, _ in pairs])
    ly = np.log([y for _, y in pairs])
    if float(np.std(lx)) == 0.0 or float(np.std(ly)) == 0.0:
        return float("nan"), len(pairs)
    return float(np.corrcoef(lx, ly)[0, 1]), len(pairs)


def classify_observable(delta_q: float, ratio_small_dt: float) -> str:
    if delta_q < 0.4 and (math.isnan(ratio_small_dt) or ratio_small_dt < 1.5):
        return "blind"
    if delta_q > 0.7 and ratio_small_dt > 3.0:
        return "sensitive"
    return "intermediate"


def compute_one_observable(
    observable: str,
    scan_rows: List[Dict[str, str]],
    fit_rows: List[Dict[str, str]],
) -> Dict[str, float | int | str]:
    q1: List[float] = []
    c1: List[float] = []
    q2: List[float] = []
    c2: List[float] = []
    for row in fit_rows:
        if row["metric"] != "observable_error":
            continue
        if not row["slope"]:
            continue
        slope = float(row["slope"])
        prefactor = float(row["prefactor"])
        if row["method"] == "trotter1":
            q1.append(slope)
            c1.append(prefactor)
        elif row["method"] == "trotter2":
            q2.append(slope)
            c2.append(prefactor)

    if not q1 or not q2:
        raise ValueError(f"No observable_error fit rows found for '{observable}'.")

    q1_mean = mean(q1)
    q2_mean = mean(q2)
    c1_mean = mean(c1)
    c2_mean = mean(c2)
    delta_q = q2_mean - q1_mean

    non_exact = [row for row in scan_rows if row["method"] != "exact"]
    dt_min = min(float(row["dt"]) for row in non_exact)

    # Compare method errors at smallest dt, grouped by model/time/state point.
    by_key: Dict[Tuple[int, float, str, float], Dict[str, float]] = {}
    for row in non_exact:
        dt = float(row["dt"])
        if abs(dt - dt_min) > 1e-15:
            continue
        key = (
            int(row["n_sites"]),
            float(row["g"]),
            row["initial_state"],
            float(row["t_target"]),
        )
        by_key.setdefault(key, {})[row["method"]] = float(row["observable_error"])

    ratios: List[float] = []
    for values in by_key.values():
        if "trotter1" in values and "trotter2" in values and values["trotter2"] > 0.0:
            ratios.append(values["trotter1"] / values["trotter2"])
    ratio_med = median(ratios) if ratios else float("nan")

    exact_rows = [row for row in scan_rows if row["method"] == "exact"]
    d1_mean = mean(abs(float(row["defect1_obs_response"])) for row in exact_rows)
    d2_mean = mean(abs(float(row["defect2_obs_response"])) for row in exact_rows)

    p1: List[float] = []
    e1: List[float] = []
    p2: List[float] = []
    e2: List[float] = []
    for row in non_exact:
        err = float(row["observable_error"])
        if row["method"] == "trotter1":
            p1.append(float(row["defect1_predictor"]))
            e1.append(err)
        elif row["method"] == "trotter2":
            p2.append(float(row["defect2_predictor"]))
            e2.append(err)

    r1, n1 = pearson_log_correlation(p1, e1)
    r2, n2 = pearson_log_correlation(p2, e2)

    classification = classify_observable(delta_q=delta_q, ratio_small_dt=ratio_med)

    return {
        "observable": observable,
        "q1_mean": q1_mean,
        "c1_mean": c1_mean,
        "q2_mean": q2_mean,
        "c2_mean": c2_mean,
        "delta_q": delta_q,
        "ratio_med_dtmin": ratio_med,
        "defect1_response_mean": d1_mean,
        "defect2_response_mean": d2_mean,
        "corr_r1": r1,
        "corr_r2": r2,
        "corr_n1": n1,
        "corr_n2": n2,
        "qualitative_class": classification,
    }


def write_markdown(path: Path, rows: List[Dict[str, float | int | str]]) -> None:
    lines: List[str] = []
    lines.append("# Week-3 Observable Sensitivity Table")
    lines.append("")
    lines.append("Date: 2026-04-23")
    lines.append("")
    lines.append("Classification rule used in this draft:")
    lines.append("")
    lines.append("- `blind`: `delta_q < 0.4` and median small-`dt` error ratio `< 1.5`")
    lines.append("- `sensitive`: `delta_q > 0.7` and median small-`dt` error ratio `> 3.0`")
    lines.append("- otherwise `intermediate`")
    lines.append("")
    lines.append("| observable | trotter1 fit (q,c) | trotter2 fit (q,c) | defect proxy (mean response, r) | class |")
    lines.append("|---|---:|---:|---:|---|")

    for row in rows:
        fit1 = f"q1={float(row['q1_mean']):.3f}, c1={float(row['c1_mean']):.3e}"
        fit2 = f"q2={float(row['q2_mean']):.3f}, c2={float(row['c2_mean']):.3e}"
        proxy = (
            f"<D1>={float(row['defect1_response_mean']):.3e}, "
            f"<D2>={float(row['defect2_response_mean']):.3e}; "
            f"r1={float(row['corr_r1']):.3f}, r2={float(row['corr_r2']):.3f}"
        )
        lines.append(
            f"| `{row['observable']}` | {fit1} | {fit2} | {proxy} | **{row['qualitative_class']}** |"
        )

    lines.append("")
    lines.append("Supporting metrics (`delta_q`, median small-`dt` ratio):")
    lines.append("")
    for row in rows:
        lines.append(
            f"- `{row['observable']}`: delta_q={float(row['delta_q']):.3f}, "
            f"median_ratio_dtmin={float(row['ratio_med_dtmin']):.3f}"
        )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    results_dir = Path(args.results_dir)
    observable_specs = parse_observable_specs(args.observables)

    table_rows: List[Dict[str, float | int | str]] = []
    for observable, scan_name, fit_name in observable_specs:
        scan_path = results_dir / scan_name
        fit_path = results_dir / fit_name
        with scan_path.open("r", encoding="utf-8", newline="") as handle:
            scan_rows = list(csv.DictReader(handle))
        with fit_path.open("r", encoding="utf-8", newline="") as handle:
            fit_rows = list(csv.DictReader(handle))
        table_rows.append(
            compute_one_observable(
                observable=observable,
                scan_rows=scan_rows,
                fit_rows=fit_rows,
            )
        )

    csv_path = results_dir / args.output_csv
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table_rows[0].keys()))
        writer.writeheader()
        writer.writerows(table_rows)

    md_path = results_dir / args.output_md
    write_markdown(md_path, table_rows)

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
