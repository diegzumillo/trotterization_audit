from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

import numpy as np


def expectation(state: np.ndarray, operator: np.ndarray) -> float:
    value = np.vdot(state, operator @ state)
    return float(np.real(value))


def state_infidelity(reference: np.ndarray, trial: np.ndarray) -> float:
    overlap = np.vdot(reference, trial)
    fidelity = float(np.abs(overlap) ** 2)
    return max(0.0, 1.0 - fidelity)


def gauss_sector_signs(reference_state: np.ndarray, generators: Iterable[np.ndarray]) -> Sequence[float]:
    signs = []
    for generator in generators:
        sign = 1.0 if expectation(reference_state, generator) >= 0.0 else -1.0
        signs.append(sign)
    return signs


def gauss_violation(
    state: np.ndarray,
    generators: Sequence[np.ndarray],
    target_signs: Sequence[float],
) -> float:
    if len(generators) != len(target_signs):
        raise ValueError("generators and target_signs must have equal length.")

    deviations = []
    for sign, generator in zip(target_signs, generators):
        value = expectation(state, generator)
        deviations.append(abs(value - sign))
    return float(np.mean(deviations)) if deviations else 0.0


def fit_power_law(dts: Sequence[float], errors: Sequence[float]) -> Optional[Tuple[float, float, int]]:
    filtered = [(dt, err) for dt, err in zip(dts, errors) if dt > 0.0 and err > 0.0]
    if len(filtered) < 2:
        return None

    log_dt = np.log([dt for dt, _ in filtered])
    log_err = np.log([err for _, err in filtered])
    slope, intercept = np.polyfit(log_dt, log_err, 1)
    prefactor = float(np.exp(intercept))
    return float(slope), prefactor, len(filtered)
