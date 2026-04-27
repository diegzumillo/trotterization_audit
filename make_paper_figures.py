from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"


def _read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _dedup_state_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []
    for row in rows:
        method = row["method"]
        if method not in {"trotter1", "trotter2"}:
            continue
        key = (
            row["n_sites"],
            row["j"],
            row["g"],
            row["m"],
            row["initial_state"],
            row["t_target"],
            row["dt"],
            row["method"],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _loglog_fit(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    lx = np.log10(x)
    ly = np.log10(y)
    slope, intercept = np.polyfit(lx, ly, 1)
    return float(slope), float(intercept)


def make_state_scaling_figure() -> None:
    rows = _read_rows(RESULTS_DIR / "week2_scan.csv")
    rows = _dedup_state_rows(rows)

    methods = [
        ("trotter1", "#1f77b4", "First-order"),
        ("trotter2", "#d62728", "Second-order"),
    ]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(6.6, 4.6), constrained_layout=True)

    for method, color, label in methods:
        method_rows = [r for r in rows if r["method"] == method]
        dts = sorted({float(r["dt"]) for r in method_rows}, reverse=True)

        medians = []
        q25 = []
        q75 = []
        for dt in dts:
            vals = np.array(
                [float(r["state_error"]) for r in method_rows if float(r["dt"]) == dt],
                dtype=float,
            )
            medians.append(float(np.median(vals)))
            q25.append(float(np.quantile(vals, 0.25)))
            q75.append(float(np.quantile(vals, 0.75)))

        x = np.array(dts, dtype=float)
        y = np.array(medians, dtype=float)
        q25_arr = np.array(q25, dtype=float)
        q75_arr = np.array(q75, dtype=float)

        slope, intercept = _loglog_fit(x, y)
        y_fit = 10 ** (intercept + slope * np.log10(x))

        ax.fill_between(x, q25_arr, q75_arr, color=color, alpha=0.15, linewidth=0.0)
        ax.plot(x, y, "o-", color=color, linewidth=2.0, markersize=5, label=f"{label} median")
        ax.plot(
            x,
            y_fit,
            "--",
            color=color,
            linewidth=1.5,
            label=fr"{label} fit ($p={slope:.3f}$)",
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"Trotter step $\Delta t$")
    ax.set_ylabel("State error")
    ax.set_title("State-level order recovery across dense $n=3,4$ scan")
    ax.legend(loc="upper left", frameon=True)

    out_pdf = FIG_DIR / "figure_state_scaling.pdf"
    out_png = FIG_DIR / "figure_state_scaling.png"
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_defect_proxy_scatter_figure() -> None:
    rows = _read_rows(RESULTS_DIR / "week2_scan.csv")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), constrained_layout=True)

    configs = [
        ("trotter1", "defect1_predictor", "First-order: $\\epsilon_O$ vs $S_1$ predictor", "#1f77b4"),
        ("trotter2", "defect2_predictor", "Second-order: $\\epsilon_O$ vs $S_2$ predictor", "#d62728"),
    ]

    for ax, (method, xkey, title, color) in zip(axes, configs):
        x_vals = []
        y_vals = []
        for row in rows:
            if row["method"] != method:
                continue
            x = float(row[xkey])
            y = float(row["observable_error"])
            if x <= 0.0 or y <= 0.0:
                continue
            x_vals.append(x)
            y_vals.append(y)

        x_arr = np.array(x_vals, dtype=float)
        y_arr = np.array(y_vals, dtype=float)

        slope, intercept = _loglog_fit(x_arr, y_arr)
        r = float(np.corrcoef(np.log10(x_arr), np.log10(y_arr))[0, 1])

        sort_idx = np.argsort(x_arr)
        x_sorted = x_arr[sort_idx]
        y_fit = 10 ** (intercept + slope * np.log10(x_sorted))

        ax.scatter(x_arr, y_arr, s=18, alpha=0.45, color=color, edgecolors="none")
        ax.plot(x_sorted, y_fit, color="black", linewidth=1.6, linestyle="--")

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("Defect predictor")
        ax.set_ylabel("Observable error")
        ax.text(
            0.03,
            0.05,
            f"$r={r:.3f}$\n$p={slope:.3f}$\n$n={x_arr.size}$",
            transform=ax.transAxes,
            fontsize=9.5,
            bbox={"facecolor": "white", "edgecolor": "#666666", "alpha": 0.85, "pad": 3.0},
        )

    out_pdf = FIG_DIR / "figure_defect_proxy_scatter.pdf"
    out_png = FIG_DIR / "figure_defect_proxy_scatter.png"
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    make_state_scaling_figure()
    make_defect_proxy_scatter_figure()
    print(f"Wrote figures to: {FIG_DIR}")


if __name__ == "__main__":
    main()
