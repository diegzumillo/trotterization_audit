from __future__ import annotations

from dataclasses import dataclass
from typing import List

import scipy.sparse as sp

from .model import Z2ModelParams
from .operators import COMPLEX_DTYPE


def _kron_many_sparse(factors: List[sp.spmatrix]) -> sp.csr_matrix:
    if not factors:
        raise ValueError("Expected at least one factor for Kronecker product.")
    result = factors[0]
    for factor in factors[1:]:
        result = sp.kron(result, factor, format="csr")
    return result.tocsr()


def _build_single_qubit_paulis_sparse(n_qubits: int):
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1.")

    i2 = sp.eye(2, dtype=COMPLEX_DTYPE, format="csr")
    x = sp.csr_matrix([[0, 1], [1, 0]], dtype=COMPLEX_DTYPE)
    z = sp.csr_matrix([[1, 0], [0, -1]], dtype=COMPLEX_DTYPE)

    x_ops: List[sp.csr_matrix] = []
    z_ops: List[sp.csr_matrix] = []

    for target in range(n_qubits):
        factors_x: List[sp.spmatrix] = []
        factors_z: List[sp.spmatrix] = []
        for qubit in range(n_qubits):
            if qubit == target:
                factors_x.append(x)
                factors_z.append(z)
            else:
                factors_x.append(i2)
                factors_z.append(i2)
        x_ops.append(_kron_many_sparse(factors_x))
        z_ops.append(_kron_many_sparse(factors_z))

    identity = sp.eye(2**n_qubits, dtype=COMPLEX_DTYPE, format="csr")
    return x_ops, z_ops, identity


class Z2ToyModelSparse:
    """Sparse 1+1D periodic Z2 gauge toy model for Krylov evolution."""

    MAX_SPARSE_DIM = 16384

    def __init__(self, params: Z2ModelParams) -> None:
        if params.n_sites < 2:
            raise ValueError("n_sites must be >= 2.")

        self.params = params
        self.n_sites = params.n_sites
        self.n_links = params.n_sites
        self.n_qubits = self.n_sites + self.n_links
        self.dim = 2**self.n_qubits

        if self.dim > self.MAX_SPARSE_DIM:
            raise ValueError(
                f"Sparse baseline supports dim <= {self.MAX_SPARSE_DIM}. "
                f"Got dim={self.dim}; reduce n_sites or increase the sparse cap."
            )

        self.x_ops, self.z_ops, self.identity = _build_single_qubit_paulis_sparse(self.n_qubits)

        self.h_mass = sp.csr_matrix((self.dim, self.dim), dtype=COMPLEX_DTYPE)
        self.h_electric = sp.csr_matrix((self.dim, self.dim), dtype=COMPLEX_DTYPE)
        self.h_hop = sp.csr_matrix((self.dim, self.dim), dtype=COMPLEX_DTYPE)

        self._build_hamiltonian_terms()

        self.h_a = (self.h_mass + self.h_electric).tocsr()
        self.h_b = self.h_hop.tocsr()
        self.h_total = (self.h_a + self.h_b).tocsr()

    def matter_index(self, site: int) -> int:
        return site

    def link_index(self, link: int) -> int:
        return self.n_sites + link

    def _build_hamiltonian_terms(self) -> None:
        for site in range(self.n_sites):
            matter_i = self.matter_index(site)
            link_i = self.link_index(site)
            next_site = (site + 1) % self.n_sites

            self.h_mass = self.h_mass + self.params.m * ((-1) ** site) * self.z_ops[matter_i]
            self.h_electric = self.h_electric + self.params.g * self.x_ops[link_i]
            self.h_hop = self.h_hop + (
                -self.params.j
                * self.x_ops[matter_i]
                @ self.z_ops[link_i]
                @ self.x_ops[self.matter_index(next_site)]
            )

        self.h_mass = self.h_mass.tocsr()
        self.h_electric = self.h_electric.tocsr()
        self.h_hop = self.h_hop.tocsr()

    def staggered_magnetization_operator(self):
        op = sp.csr_matrix((self.dim, self.dim), dtype=COMPLEX_DTYPE)
        for site in range(self.n_sites):
            op = op + ((-1) ** site) * self.z_ops[self.matter_index(site)]
        return (op / self.n_sites).tocsr()

    def gauss_generators(self):
        generators = []
        for site in range(self.n_sites):
            left_link = self.link_index((site - 1) % self.n_sites)
            right_link = self.link_index(site)
            generators.append(
                (
                    self.z_ops[self.matter_index(site)]
                    @ self.x_ops[left_link]
                    @ self.x_ops[right_link]
                ).tocsr()
            )
        return generators
