from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .operators import COMPLEX_DTYPE, build_single_qubit_paulis


@dataclass(frozen=True)
class Z2ModelParams:
    n_sites: int
    j: float = 1.0
    g: float = 1.0
    m: float = 0.5


class Z2ToyModel:
    """Dense 1+1D periodic Z2 gauge toy model for very small systems."""

    MAX_DENSE_DIM = 512

    def __init__(self, params: Z2ModelParams) -> None:
        if params.n_sites < 2:
            raise ValueError("n_sites must be >= 2.")

        self.params = params
        self.n_sites = params.n_sites
        self.n_links = params.n_sites
        self.n_qubits = self.n_sites + self.n_links
        self.dim = 2**self.n_qubits

        if self.dim > self.MAX_DENSE_DIM:
            raise ValueError(
                f"Dense baseline supports dim <= {self.MAX_DENSE_DIM}. "
                f"Got dim={self.dim}; reduce n_sites."
            )

        paulis = build_single_qubit_paulis(self.n_qubits)
        self.x_ops: List[np.ndarray] = paulis["x"]  # type: ignore[assignment]
        self.z_ops: List[np.ndarray] = paulis["z"]  # type: ignore[assignment]
        self.identity: np.ndarray = paulis["identity"]  # type: ignore[assignment]

        self.h_mass = np.zeros((self.dim, self.dim), dtype=COMPLEX_DTYPE)
        self.h_electric = np.zeros((self.dim, self.dim), dtype=COMPLEX_DTYPE)
        self.h_hop = np.zeros((self.dim, self.dim), dtype=COMPLEX_DTYPE)

        self._build_hamiltonian_terms()

        self.h_a = self.h_mass + self.h_electric
        self.h_b = self.h_hop
        self.h_total = self.h_a + self.h_b

    def matter_index(self, site: int) -> int:
        return site

    def link_index(self, link: int) -> int:
        return self.n_sites + link

    def _build_hamiltonian_terms(self) -> None:
        for site in range(self.n_sites):
            matter_i = self.matter_index(site)
            link_i = self.link_index(site)
            next_site = (site + 1) % self.n_sites

            self.h_mass += self.params.m * ((-1) ** site) * self.z_ops[matter_i]
            self.h_electric += self.params.g * self.x_ops[link_i]
            self.h_hop += (
                -self.params.j
                * self.x_ops[matter_i]
                @ self.z_ops[link_i]
                @ self.x_ops[self.matter_index(next_site)]
            )

    def staggered_magnetization_operator(self) -> np.ndarray:
        op = np.zeros((self.dim, self.dim), dtype=COMPLEX_DTYPE)
        for site in range(self.n_sites):
            op += ((-1) ** site) * self.z_ops[self.matter_index(site)]
        return op / self.n_sites

    def gauss_generators(self) -> List[np.ndarray]:
        generators: List[np.ndarray] = []
        for site in range(self.n_sites):
            left_link = self.link_index((site - 1) % self.n_sites)
            right_link = self.link_index(site)
            generators.append(
                self.z_ops[self.matter_index(site)]
                @ self.x_ops[left_link]
                @ self.x_ops[right_link]
            )
        return generators
