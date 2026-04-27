from __future__ import annotations

from typing import Iterable, List

import numpy as np

from .operators import COMPLEX_DTYPE
from .model import Z2ToyModel


def product_state_from_bits(bits: Iterable[int]) -> np.ndarray:
    vectors: List[np.ndarray] = []
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError(f"Bits must be 0/1, got {bit}.")
        if bit == 0:
            vectors.append(np.array([1.0, 0.0], dtype=COMPLEX_DTYPE))
        else:
            vectors.append(np.array([0.0, 1.0], dtype=COMPLEX_DTYPE))

    if not vectors:
        raise ValueError("Expected at least one qubit bit.")

    state = vectors[0]
    for vector in vectors[1:]:
        state = np.kron(state, vector)
    return state


def product_state_from_labels(labels: Iterable[str]) -> np.ndarray:
    inv_sqrt_two = 1.0 / np.sqrt(2.0)
    basis = {
        "z+": np.array([1.0, 0.0], dtype=COMPLEX_DTYPE),
        "z-": np.array([0.0, 1.0], dtype=COMPLEX_DTYPE),
        "x+": np.array([inv_sqrt_two, inv_sqrt_two], dtype=COMPLEX_DTYPE),
        "x-": np.array([inv_sqrt_two, -inv_sqrt_two], dtype=COMPLEX_DTYPE),
    }

    vectors: List[np.ndarray] = []
    for label in labels:
        if label not in basis:
            raise ValueError(f"Unknown single-qubit label '{label}'.")
        vectors.append(basis[label])

    if not vectors:
        raise ValueError("Expected at least one qubit label.")

    state = vectors[0]
    for vector in vectors[1:]:
        state = np.kron(state, vector)
    return state


def neel_matter_up_links(model: Z2ToyModel) -> np.ndarray:
    matter_bits = [site % 2 for site in range(model.n_sites)]
    link_bits = [0 for _ in range(model.n_links)]
    return product_state_from_bits(matter_bits + link_bits)


def neel_matter_plus_links_x(model: Z2ToyModel) -> np.ndarray:
    labels: List[str] = []
    for site in range(model.n_sites):
        labels.append("z+" if (site % 2 == 0) else "z-")
    for _ in range(model.n_links):
        labels.append("x+")
    return product_state_from_labels(labels)


def uniform_matter_plus_links_x(model: Z2ToyModel) -> np.ndarray:
    labels = ["z+" for _ in range(model.n_sites)]
    labels.extend("x+" for _ in range(model.n_links))
    return product_state_from_labels(labels)


def domain_wall_matter_plus_links_x(model: Z2ToyModel) -> np.ndarray:
    labels: List[str] = []
    midpoint = model.n_sites // 2
    for site in range(model.n_sites):
        labels.append("z+" if site < midpoint else "z-")
    for _ in range(model.n_links):
        labels.append("x+")
    return product_state_from_labels(labels)
