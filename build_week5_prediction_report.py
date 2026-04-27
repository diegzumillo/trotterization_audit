from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple


OBSERVABLES = (
    "h_hop_density",
    "electric_density",
    "staggered_magnetization",
    "mass_density",
    "total_energy_density",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write week-5 analytic-prediction and algebra-vs-numerics reports."
    )
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--algebra-csv", default="week5_split_algebra.csv")
    parser.add_argument("--numerics-csv", default="week5_probe_original_swapped_table.csv")
    parser.add_argument("--prediction-md", default="week5_analytic_predictions.md")
    parser.add_argument("--comparison-md", default="week5_algebra_numeric_comparison.md")
    return parser.parse_args()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def short_class(class_name: str) -> str:
    mapping = {
        "leading-defect sensitive": "sensitive",
        "state-suppressed blind": "state-suppressed blind",
        "algebraically suppressed but state-sensitive": "second-layer state-sensitive",
        "fully blind": "fully blind",
    }
    return mapping.get(class_name, class_name)


def prediction_changed(a: str, b: str) -> str:
    return "yes" if short_class(a) != short_class(b) else "no"


def write_prediction_report(
    path: Path,
    algebra_by_key: Dict[Tuple[str, str], Dict[str, str]],
) -> None:
    lines: List[str] = []
    lines.append("# Week-5 Analytic Predictions")
    lines.append("")
    lines.append("Date: 2026-04-25")
    lines.append("")
    lines.append(
        "This report freezes the pre-scan algebraic predictions for the original and swapped "
        "Hamiltonian splits. The table is intentionally separate from numerical outcomes so the "
        "reduced-grid scans test predictions rather than define them."
    )
    lines.append("")
    lines.append("| observable | Split I algebraic class | Split II algebraic class | prediction change? |")
    lines.append("|---|---|---|---|")
    for observable in OBSERVABLES:
        original = algebra_by_key[(observable, "original")]["class"]
        swapped = algebra_by_key[(observable, "swapped")]["class"]
        lines.append(
            f"| `{observable}` | {short_class(original)} | {short_class(swapped)} | "
            f"**{prediction_changed(original, swapped)}** |"
        )
    lines.append("")
    lines.append("Centerpiece prediction:")
    lines.append("")
    lines.append(
        "Physically natural Hamiltonian regroupings move observables between algebraic classes, "
        "and numerical visibility should track the class rather than the observable identity."
    )
    lines.append("")
    lines.append("Important refinement:")
    lines.append("")
    lines.append(
        "`h_hop_density` is not predicted to become fully blind under Split II. It moves from "
        "leading-defect sensitive to the second-layer state-sensitive class: `[O,H_A]=0`, but "
        "`[H_A,[H_B,O]]` is nonzero and has nonzero product-state expectation in the current check."
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_comparison_report(
    path: Path,
    algebra_by_key: Dict[Tuple[str, str], Dict[str, str]],
    numeric_by_key: Dict[Tuple[str, str], Dict[str, str]],
) -> None:
    lines: List[str] = []
    lines.append("# Week-5 Algebra vs Numerical Visibility")
    lines.append("")
    lines.append("Date: 2026-04-25")
    lines.append("")
    lines.append(
        "Reduced-grid protocol: `n_sites=3`, `g=1.0`, states `neel_x,uniform_x`, "
        "`t_final={0.5,1.0}`, `dt={0.5,0.25,0.125,0.0625}`."
    )
    lines.append("")
    lines.append("| observable | split | algebraic class | numerical class | dq | ratio E1/E2 | readout |")
    lines.append("|---|---|---|---|---:|---:|---|")
    for observable in OBSERVABLES:
        for split_name in ("original", "swapped"):
            algebra = algebra_by_key[(observable, split_name)]["class"]
            numeric = numeric_by_key[(observable, split_name)]
            dq = float(numeric["delta_q_mean"])
            ratio = float(numeric["ratio_small_dt_median_e1_over_e2"])
            numeric_class = numeric["class"]
            readout = "aligned"
            if short_class(algebra) == "sensitive" and numeric_class != "sensitive":
                readout = "state/protocol suppressed"
            elif short_class(algebra) != "sensitive" and numeric_class == "sensitive":
                readout = "visible beyond leading class"
            lines.append(
                f"| `{observable}` | `{split_name}` | {short_class(algebra)} | "
                f"**{numeric_class}** | {dq:.3f} | {ratio:.3g} | {readout} |"
            )
    lines.append("")
    lines.append("Interpretation:")
    lines.append("")
    lines.append(
        "The three-class algebra is doing useful work, but the reduced product-state numerics show "
        "that operator-level sensitivity is not automatically visible in this protocol. This makes "
        "the planned second-layer state test essential rather than optional."
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    results_dir = Path(args.results_dir)
    algebra_rows = read_csv(results_dir / args.algebra_csv)
    numeric_rows = read_csv(results_dir / args.numerics_csv)

    algebra_by_key = {
        (row["observable"], row["split"]): row
        for row in algebra_rows
        if row["split"] in ("original", "swapped")
    }
    numeric_by_key = {
        (row["observable"], row["split"]): row
        for row in numeric_rows
        if row["split"] in ("original", "swapped")
    }

    write_prediction_report(results_dir / args.prediction_md, algebra_by_key)
    write_comparison_report(results_dir / args.comparison_md, algebra_by_key, numeric_by_key)

    print(f"Wrote {results_dir / args.prediction_md}")
    print(f"Wrote {results_dir / args.comparison_md}")


if __name__ == "__main__":
    main()
