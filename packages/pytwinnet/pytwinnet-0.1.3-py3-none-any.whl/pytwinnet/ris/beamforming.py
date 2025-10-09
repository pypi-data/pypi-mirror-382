from __future__ import annotations
import numpy as np
from typing import Tuple

class RISPanel:
    """Planar RIS with N elements and per-element phase shifts."""
    def __init__(self, n_elements: int, element_gain_linear: float = 1.0, seed: int | None = None):
        self.N = int(n_elements)
        self.g = float(element_gain_linear)
        self.rng = np.random.default_rng(seed)
        # phases in radians
        self.theta = np.zeros(self.N, dtype=float)

    def set_phases(self, theta_rad: np.ndarray) -> None:
        assert theta_rad.shape == (self.N,)
        self.theta = np.mod(theta_rad, 2*np.pi)

    def randomize(self) -> None:
        self.theta = self.rng.uniform(0, 2*np.pi, size=self.N)

def ris_link_gain(h_tx_ris: np.ndarray, h_ris_rx: np.ndarray, theta: np.ndarray) -> complex:
    """
    Effective scalar channel h_eff = sum_n h_ris_rx[n] * e^{j theta[n]} * h_tx_ris[n].
    Args:
        h_tx_ris: (N,) complex, TX->RIS
        h_ris_rx: (N,) complex, RIS->RX
        theta:    (N,) phases
    """
    return np.sum(h_ris_rx * np.exp(1j*theta) * h_tx_ris)

def phase_opt_greedy(h_tx_ris: np.ndarray, h_ris_rx: np.ndarray, iters: int = 2) -> np.ndarray:
    """
    Greedy per-element phase alignment (fast baseline).
    Align each element's phase to maximize |h_eff|.
    """
    N = h_tx_ris.size
    theta = np.zeros(N, dtype=float)
    prod = h_ris_rx * h_tx_ris
    theta = -np.angle(prod)
    for _ in range(max(0, iters-1)):
        pass
    return np.mod(theta, 2*np.pi)

# Usage
# from pytwinnet.ris import RISPanel, ris_link_gain, phase_opt_greedy
# from pytwinnet.mimo import mimo_rayleigh

# N = 64
# H_tr = mimo_rayleigh(nt=N, nr=1)[:,0]   # TX->RIS (N,)
# H_rr = mimo_rayleigh(nt=1, nr=N)[0,:]   # RIS->RX (N,)
# panel = RISPanel(N)
# theta = phase_opt_greedy(H_tr, H_rr)
# panel.set_phases(theta)
# h_eff = ris_link_gain(H_tr, H_rr, panel.theta)  # complex scalar channel via RIS

