from __future__ import annotations

from typing import Dict, List

import numpy as np

COMPLEX_DTYPE = np.complex128
I2 = np.eye(2, dtype=COMPLEX_DTYPE)
X = np.array([[0, 1], [1, 0]], dtype=COMPLEX_DTYPE)
Z = np.array([[1, 0], [0, -1]], dtype=COMPLEX_DTYPE)


def kron_many(factors: List[np.ndarray]) -> np.ndarray:
    if not factors:
        raise ValueError("Expected at least one factor for Kronecker product.")
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def build_single_qubit_paulis(n_qubits: int) -> Dict[str, List[np.ndarray] | np.ndarray]:
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1.")

    x_ops: List[np.ndarray] = []
    z_ops: List[np.ndarray] = []

    for target in range(n_qubits):
        factors_x: List[np.ndarray] = []
        factors_z: List[np.ndarray] = []
        for qubit in range(n_qubits):
            if qubit == target:
                factors_x.append(X)
                factors_z.append(Z)
            else:
                factors_x.append(I2)
                factors_z.append(I2)
        x_ops.append(kron_many(factors_x))
        z_ops.append(kron_many(factors_z))

    identity = np.eye(2**n_qubits, dtype=COMPLEX_DTYPE)
    return {"x": x_ops, "z": z_ops, "identity": identity}
