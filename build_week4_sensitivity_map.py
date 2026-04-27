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
        description="Freeze canonical week-4 sensitivity map from existing scan artifacts."
    )
    parser.add_argument("--results-dir", default="results", help="Directory with CSV artifacts")
    parser.add_argument(
        "--observables",
        default=(
            "h_hop_density:week2_scan.csv:week2_fits.csv,"
            "electric_density:week3_electric_scan.csv:week3_electric_fits.csv,"
            "staggered_magnetization:week3_staggered_scan.csv:week3_staggered_fits.csv,"
            "mass_density:week3_mass_scan.csv:week3_mass_fits.csv,"
            "total_energy_density:week3_total_energy_scan.csv:week3_total_energy_fits.csv"
        ),
        help="Comma-separated list observable:scan_csv:fit_csv",
    )
    parser.add_argument(
        "--output-csv",
        default="week4_sensitivity_map.csv",
        help="Output CSV filename (inside results dir)",
    )
    parser.add_argument(
        "--output-md",
        default="week4_sensitivity_map.md",
        help="Output markdown filename (inside results dir)",
    )
    parser.add_argument(
        "--output-note",
        default="week4_centerpiece_note.md",
        help="Output note filename (inside results dir)",
    )
    return parser.parse_args()


def parse_observable_specs(raw: str) -> List[Tuple[str, str, str]]:
    specs: List[Tuple[str, str, str]] = []
    for part in raw.split(","):
        item = part.strip()
        if not item:
            continue
        fields = item.split(":")
        if len(fields) != 3:
            raise ValueError(
                f"Invalid spec '{item}'. Expected observable:scan.csv:fit.csv"
            )
        specs.append((fields[0], fields[1], fields[2]))
    if not specs:
        raise ValueError("No observable specs provided.")
    return specs


def stats(values: Sequence[float]) -> Tuple[float, float, float]:
    return mean(values), min(values), max(values)


def pearson_log(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, int]:
    pairs = [(x, y) for x, y in zip(xs, ys) if x > 0.0 and y > 0.0]
    if len(pairs) < 2:
        return float("nan"), 0
    lx = np.log([x for x, _ in pairs])
    ly = np.log([y for _, y in pairs])
    if float(np.std(lx)) == 0.0 or float(np.std(ly)) == 0.0:
        return float("nan"), len(pairs)
    return float(np.corrcoef(lx, ly)[0, 1]), len(pairs)


def classify(delta_q_mean: float, ratio_small_dt_median: float) -> str:
    if delta_q_mean < 0.4 and (math.isnan(ratio_small_dt_median) or ratio_small_dt_median < 1.5):
        return "blind"
    if delta_q_mean > 0.7 and ratio_small_dt_median > 3.0:
        return "sensitive"
    return "intermediate"


def compute_row(observable: str, scan_rows: List[Dict[str, str]], fit_rows: List[Dict[str, str]]) -> Dict[str, float | int | str]:
    q1_vals: List[float] = []
    c1_vals: List[float] = []
    q2_vals: List[float] = []
    c2_vals: List[float] = []

    for row in fit_rows:
        if row["metric"] != "observable_error":
            continue
        if not row["slope"]:
            continue
        q = float(row["slope"])
        c = float(row["prefactor"])
        if row["method"] == "trotter1":
            q1_vals.append(q)
            c1_vals.append(c)
        elif row["method"] == "trotter2":
            q2_vals.append(q)
            c2_vals.append(c)

    if not q1_vals or not q2_vals:
        raise ValueError(f"Missing observable_error fit rows for '{observable}'.")

    q1_mean, q1_min, q1_max = stats(q1_vals)
    q2_mean, q2_min, q2_max = stats(q2_vals)
    c1_mean, c1_min, c1_max = stats(c1_vals)
    c2_mean, c2_min, c2_max = stats(c2_vals)
    delta_q_mean = q2_mean - q1_mean

    non_exact = [row for row in scan_rows if row["method"] != "exact"]
    dt_min = min(float(row["dt"]) for row in non_exact)

    # At smallest dt, compute median ratio E1/E2 across all (n,g,state,t_target)
    keyed: Dict[Tuple[int, float, str, float], Dict[str, float]] = {}
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
        keyed.setdefault(key, {})[row["method"]] = float(row["observable_error"])

    ratios: List[float] = []
    for values in keyed.values():
        if "trotter1" in values and "trotter2" in values and values["trotter2"] > 0.0:
            ratios.append(values["trotter1"] / values["trotter2"])
    ratio_small_dt_median = median(ratios) if ratios else float("nan")

    exact_rows = [row for row in scan_rows if row["method"] == "exact"]
    d1_vals = [abs(float(row["defect1_obs_response"])) for row in exact_rows]
    d2_vals = [abs(float(row["defect2_obs_response"])) for row in exact_rows]
    d1_mean, d1_min, d1_max = stats(d1_vals)
    d2_mean, d2_min, d2_max = stats(d2_vals)

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

    corr_r1, corr_n1 = pearson_log(p1, e1)
    corr_r2, corr_n2 = pearson_log(p2, e2)

    return {
        "observable": observable,
        "q1_mean": q1_mean,
        "q1_min": q1_min,
        "q1_max": q1_max,
        "q2_mean": q2_mean,
        "q2_min": q2_min,
        "q2_max": q2_max,
        "delta_q_mean": delta_q_mean,
        "c1_mean": c1_mean,
        "c1_min": c1_min,
        "c1_max": c1_max,
        "c2_mean": c2_mean,
        "c2_min": c2_min,
        "c2_max": c2_max,
        "ratio_small_dt_median_e1_over_e2": ratio_small_dt_median,
        "defect1_response_mean": d1_mean,
        "defect1_response_min": d1_min,
        "defect1_response_max": d1_max,
        "defect2_response_mean": d2_mean,
        "defect2_response_min": d2_min,
        "defect2_response_max": d2_max,
        "corr_r1": corr_r1,
        "corr_n1": corr_n1,
        "corr_r2": corr_r2,
        "corr_n2": corr_n2,
        "class": classify(delta_q_mean, ratio_small_dt_median),
    }


def write_markdown(path: Path, rows: List[Dict[str, float | int | str]]) -> None:
    lines: List[str] = []
    lines.append("# Week-4 Sensitivity Map")
    lines.append("")
    lines.append("Date: 2026-04-23")
    lines.append("")
    lines.append(
        "Canonical table built from week-2/week-3 scan artifacts over "
        "`n_sites={3,4}`, `g={0.5,1.0,1.5}`, "
        "`t_target={0.5,1.0,2.0,4.0}`, `dt={0.5,0.25,0.125,0.0625,0.03125}`, "
        "and states `neel_x, uniform_x, domain_wall_x`."
    )
    lines.append("")
    lines.append("Class thresholds used:")
    lines.append("")
    lines.append("- `blind`: `delta_q_mean < 0.4` and median small-`dt` ratio `< 1.5`")
    lines.append("- `sensitive`: `delta_q_mean > 0.7` and median small-`dt` ratio `> 3.0`")
    lines.append("- otherwise `intermediate`")
    lines.append("")
    lines.append("| observable | slopes `(q1,q2)` mean[min,max] | prefactors `(c1,c2)` mean[min,max] | defect proxy + corr | class |")
    lines.append("|---|---:|---:|---:|---|")

    for row in rows:
        slopes = (
            f"q1={float(row['q1_mean']):.3f}[{float(row['q1_min']):.3f},{float(row['q1_max']):.3f}], "
            f"q2={float(row['q2_mean']):.3f}[{float(row['q2_min']):.3f},{float(row['q2_max']):.3f}]"
        )
        prefs = (
            f"c1={float(row['c1_mean']):.3e}[{float(row['c1_min']):.3e},{float(row['c1_max']):.3e}], "
            f"c2={float(row['c2_mean']):.3e}[{float(row['c2_min']):.3e},{float(row['c2_max']):.3e}]"
        )
        proxy = (
            f"<D1>={float(row['defect1_response_mean']):.3e}, "
            f"<D2>={float(row['defect2_response_mean']):.3e}, "
            f"r1={float(row['corr_r1']):.3f}, r2={float(row['corr_r2']):.3f}, "
            f"ratio_dtmin={float(row['ratio_small_dt_median_e1_over_e2']):.3f}"
        )
        lines.append(f"| `{row['observable']}` | {slopes} | {prefs} | {proxy} | **{row['class']}** |")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_note(path: Path, rows: List[Dict[str, float | int | str]]) -> None:
    sensitive = [str(row["observable"]) for row in rows if row["class"] == "sensitive"]
    blind = [str(row["observable"]) for row in rows if row["class"] == "blind"]
    intermediate = [str(row["observable"]) for row in rows if row["class"] == "intermediate"]

    lines: List[str] = []
    lines.append("# Week-4 Centerpiece Note")
    lines.append("")
    lines.append("Date: 2026-04-23")
    lines.append("")
    lines.append("This note freezes the sensitivity-map table as the current center result.")
    lines.append("")
    lines.append("Readout:")
    lines.append("")
    lines.append(f"- sensitive: {', '.join(sensitive) if sensitive else '(none)'}")
    lines.append(f"- intermediate: {', '.join(intermediate) if intermediate else '(none)'}")
    lines.append(f"- blind: {', '.join(blind) if blind else '(none)'}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("")
    lines.append("- Integrator-order visibility is observable-dependent, not uniform.")
    lines.append("- BCH-defect sensitivity tracks this visibility across channels.")
    lines.append("- This supports a defect-centered narrative for the paper.")
    lines.append("")
    lines.append("Next credibility step:")
    lines.append("")
    lines.append("- move to sparse/Krylov and test `n_sites=5` with a focused subset.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    results_dir = Path(args.results_dir)
    specs = parse_observable_specs(args.observables)

    table_rows: List[Dict[str, float | int | str]] = []
    for observable, scan_name, fit_name in specs:
        with (results_dir / scan_name).open("r", encoding="utf-8", newline="") as handle:
            scan_rows = list(csv.DictReader(handle))
        with (results_dir / fit_name).open("r", encoding="utf-8", newline="") as handle:
            fit_rows = list(csv.DictReader(handle))
        table_rows.append(compute_row(observable, scan_rows, fit_rows))

    csv_path = results_dir / args.output_csv
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table_rows[0].keys()))
        writer.writeheader()
        writer.writerows(table_rows)

    md_path = results_dir / args.output_md
    write_markdown(md_path, table_rows)

    note_path = results_dir / args.output_note
    write_note(note_path, table_rows)

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {note_path}")


if __name__ == "__main__":
    main()
