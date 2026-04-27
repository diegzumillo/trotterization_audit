from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


FIGURE_DIR = Path("results/figures")


def read_csv(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def savefig(name: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIGURE_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.savefig(FIGURE_DIR / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close()


def make_split_map() -> None:
    rows = read_csv("results/week5_probe_original_swapped_table.csv")
    observables = [
        "h_hop_density",
        "electric_density",
        "staggered_magnetization",
        "mass_density",
        "total_energy_density",
    ]
    splits = ["original", "swapped"]
    by_key = {(row["observable"], row["split"]): row for row in rows}
    values = np.array(
        [
            [
                float(by_key[(observable, split)]["ratio_small_dt_median_e1_over_e2"])
                for split in splits
            ]
            for observable in observables
        ]
    )
    log_values = np.log10(values)

    plt.figure(figsize=(5.6, 4.1))
    ax = plt.gca()
    image = ax.imshow(log_values, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(splits)), splits)
    ax.set_yticks(range(len(observables)), [label.replace("_", r"\_") for label in observables])
    ax.set_title("Split-dependent observable visibility")
    cbar = plt.colorbar(image, ax=ax)
    cbar.set_label(r"$\log_{10}$ median $E_1/E_2$")
    for i, observable in enumerate(observables):
        for j, split in enumerate(splits):
            ratio = values[i, j]
            dq = float(by_key[(observable, split)]["delta_q_mean"])
            ax.text(j, i, f"{ratio:.2g}\n$dq$={dq:.2f}", ha="center", va="center", color="white")
    savefig("week5_split_visibility_map")


def load_scan_errors(path: str, state: str, t_target: float) -> Dict[str, Tuple[List[float], List[float]]]:
    rows = read_csv(path)
    out: Dict[str, Tuple[List[float], List[float]]] = {}
    for method in ("trotter1", "trotter2"):
        pairs = []
        for row in rows:
            if row["initial_state"] != state:
                continue
            if row["method"] != method:
                continue
            if abs(float(row["t_target"]) - t_target) > 1e-12:
                continue
            pairs.append((float(row["dt"]), float(row["observable_error"])))
        pairs.sort(reverse=True)
        out[method] = ([dt for dt, _ in pairs], [err for _, err in pairs])
    return out


def make_anchor_figure() -> None:
    product = load_scan_errors(
        "results/week5_probe_swapped_h_hop_density_scan.csv",
        "neel_x",
        1.0,
    )
    ground = load_scan_errors(
        "results/week5_swapped_h_hop_density_split_a_ground_scan.csv",
        "split_a_ground",
        1.0,
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2), sharey=True)
    panels = [
        (axes[0], product, "product seed"),
        (axes[1], ground, r"$H_A$ ground state"),
    ]
    for ax, data, title in panels:
        for method, marker, label in [
            ("trotter1", "o", "first order"),
            ("trotter2", "s", "second order"),
        ]:
            dts, errors = data[method]
            ax.loglog(dts, errors, marker=marker, linewidth=1.6, label=label)
        ax.set_title(title)
        ax.set_xlabel(r"$\Delta t$")
        ax.grid(True, which="both", alpha=0.25)
    axes[0].set_ylabel(r"$|\langle O\rangle_{\rm Trotter}-\langle O\rangle_{\rm exact}|$")
    axes[0].legend(frameon=False)
    fig.suptitle(r"Swapped split, $O_{\rm hop}=H_A/n$")
    savefig("week5_hhop_anchor_effect")


def make_state_family_scatter() -> None:
    rows = read_csv("results/week5_state_family_hhop_swapped.csv")
    colors = {
        "ha_evolved": "#1f77b4",
        "h_evolved": "#d62728",
        "sector_ground_interp": "#2ca02c",
    }
    markers = {
        "ha_evolved": "o",
        "h_evolved": "s",
        "sector_ground_interp": "^",
    }

    plt.figure(figsize=(5.8, 4.2))
    ax = plt.gca()
    for family in colors:
        xs = []
        ys = []
        for row in rows:
            if row["family"] != family:
                continue
            x = float(row["nested_abs_initial"])
            y = float(row["linear_prefactor_abs_trotter1"])
            if x > 0.0 and y > 0.0:
                xs.append(x)
                ys.append(y)
        ax.loglog(xs, ys, markers[family], color=colors[family], alpha=0.75, label=family)
    ax.set_xlabel(r"$|\langle [H_A,[H_B,O]]\rangle_{\psi_0}|$")
    ax.set_ylabel(r"observed $|a_1|$ in $E_1(\Delta t)\simeq a_1\Delta t+a_2\Delta t^2$")
    ax.set_title(r"State-family diagnostic for swapped $O_{\rm hop}$")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False)
    savefig("week5_state_family_hhop_swapped")


def main() -> None:
    make_split_map()
    make_anchor_figure()
    make_state_family_scatter()
    print("Wrote week-5 figures to results/figures")


if __name__ == "__main__":
    main()
