from __future__ import annotations

import numpy as np
from scipy.linalg import expm
from scipy.sparse import issparse
from scipy.sparse.linalg import expm_multiply


def exact_evolve(hamiltonian: np.ndarray, initial_state: np.ndarray, time: float) -> np.ndarray:
    if time < 0:
        raise ValueError("time must be >= 0.")
    if issparse(hamiltonian):
        return np.asarray(expm_multiply((-1j * time) * hamiltonian, initial_state))
    unitary = expm(-1j * hamiltonian * time)
    return unitary @ initial_state


def trotter_evolve(
    initial_state: np.ndarray,
    h_a,
    h_b,
    dt: float,
    n_steps: int,
    order: int,
) -> np.ndarray:
    if dt <= 0:
        raise ValueError("dt must be > 0.")
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1.")
    if order not in (1, 2):
        raise ValueError("order must be 1 or 2.")

    psi = initial_state.copy()
    sparse_mode = issparse(h_a) or issparse(h_b)

    if sparse_mode:
        if order == 1:
            a_step = (-1j * dt) * h_a
            b_step = (-1j * dt) * h_b
            for _ in range(n_steps):
                psi = np.asarray(expm_multiply(a_step, psi))
                psi = np.asarray(expm_multiply(b_step, psi))
            return psi

        half_a_step = (-1j * 0.5 * dt) * h_a
        b_step = (-1j * dt) * h_b
        for _ in range(n_steps):
            psi = np.asarray(expm_multiply(half_a_step, psi))
            psi = np.asarray(expm_multiply(b_step, psi))
            psi = np.asarray(expm_multiply(half_a_step, psi))
        return psi

    if order == 1:
        u_a = expm(-1j * h_a * dt)
        u_b = expm(-1j * h_b * dt)
        for _ in range(n_steps):
            psi = u_b @ (u_a @ psi)
        return psi

    u_half_a = expm(-1j * h_a * (0.5 * dt))
    u_b = expm(-1j * h_b * dt)
    for _ in range(n_steps):
        psi = u_half_a @ psi
        psi = u_b @ psi
        psi = u_half_a @ psi
    return psi
