from __future__ import annotations
import numpy as np

def mimo_rayleigh(nt: int, nr: int, seed: int | None = None) -> np.ndarray:
    """i.i.d. Rayleigh flat-fading MIMO channel H (nr x nt)."""
    rng = np.random.default_rng(seed)
    H = (rng.normal(size=(nr, nt)) + 1j*rng.normal(size=(nr, nt))) / np.sqrt(2.0)
    return H

def matched_filter_tx(H: np.ndarray) -> np.ndarray:
    """Downlink: transmit beamformer for single user (nt x 1) normalized."""
    w = H.conj().T @ np.ones((H.shape[0], 1), dtype=H.dtype)
    w /= np.linalg.norm(w) + 1e-12
    return w

def zf_precoder(H: np.ndarray) -> np.ndarray:
    """Multi-user ZF precoder (nt x K) for H (K x nt)."""
    # For K users, row-stack their channels in H (K x nt) for convenience
    Hh = H.conj()
    W = Hh.T @ np.linalg.pinv(H @ Hh.T + 1e-9*np.eye(H.shape[0]))
    # column-normalize per-user streams
    W = W / (np.linalg.norm(W, axis=0, keepdims=True) + 1e-12)
    return W
