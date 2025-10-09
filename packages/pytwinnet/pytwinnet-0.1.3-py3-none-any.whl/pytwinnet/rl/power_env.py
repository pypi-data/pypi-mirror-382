from __future__ import annotations
import numpy as np
from typing import List, Dict, Tuple, Optional
from pytwinnet.accelerate.vectorized import fspl_matrix_db
from pytwinnet.core.node import WirelessNode
from pytwinnet.physics import FreeSpacePathLoss
from pytwinnet.accelerate.vectorized import (
            fspl_matrix_db, rsrp_matrix_dbm, noise_dbm_vector,
            sinr_db_from_rsrp_matrix, shannon_throughput_bps_vector
        )

class PowerControlEnv:
    """
    A lightweight, gymnasium-like environment for downlink power control.
    - Observations: per-UE RSRP (or path-loss proxy) and current TX power.
    - Actions: discrete power delta {-Δ, 0, +Δ} for each gNB (vector or per-agent).
    - Reward: sum-throughput (or weighted) minus power penalty.
    This avoids hard dependency on gym; but the API is compatible enough.
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self,
                 twin,
                 tx_ids: List[str],
                 ue_ids: List[str],
                 bandwidth_hz: float = 20e6,
                 efficiency: float = 0.75,
                 power_step_db: float = 1.0,
                 power_min_dbm: float = 10.0,
                 power_max_dbm: float = 40.0,
                 penalty_lambda: float = 0.0):
        self.twin = twin
        self.tx_ids = tx_ids
        self.ue_ids = ue_ids
        self.B = bandwidth_hz
        self.eta = efficiency
        self.step_db = power_step_db
        self.pmin = power_min_dbm
        self.pmax = power_max_dbm
        self.lmb = penalty_lambda
        self._obs = None

    # --- core loop ---
    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        # build initial observation (e.g., current tx powers + path loss snapshot)
        self._obs = self._make_obs()
        return self._obs

    def step(self, action_vector: np.ndarray):
        """
        action_vector shape = (len(tx_ids),) in {-1,0,+1}, meaning -Δ, 0, +Δ dB.
        """
        for k, tx_id in enumerate(self.tx_ids):
            node = self.twin.network.get_node_by_id(tx_id)
            p = node.transceiver_properties.transmit_power_dbm
            p_new = np.clip(p + self.step_db * float(action_vector[k]), self.pmin, self.pmax)
            node.transceiver_properties.transmit_power_dbm = float(p_new)

        # compute reward
        reward, info = self._throughput_reward()
        self._obs = self._make_obs()
        terminated, truncated = False, False
        return self._obs, reward, terminated, truncated, info

    # --- helpers ---
    def _make_obs(self):
        # example obs: [tx_powers_dbm, avg_pathloss_to_each_ue]  -> simple vector
        tx_p = []
        for tx_id in self.tx_ids:
            tx_p.append(self.twin.network.get_node_by_id(tx_id).transceiver_properties.transmit_power_dbm)
        tx_p = np.array(tx_p, dtype=float)
        # simple pathloss proxy: FSPL from each TX to a reference UE (or average over UEs)
        f = 3.5e9
        tx_xyz = []
        ue_xyz = []
        for tx_id in self.tx_ids:
            tx_xyz.append(self.twin.network.get_node_by_id(tx_id).position)
        for ue_id in self.ue_ids:
            ue_xyz.append(self.twin.network.get_node_by_id(ue_id).position)
        tx_xyz = np.array(tx_xyz, float)
        ue_xyz = np.array(ue_xyz, float)
        pl = fspl_matrix_db(tx_xyz, ue_xyz, f)  # (n_tx, n_ue)
        avg_pl = pl.mean(axis=1)  # per TX
        return np.concatenate([tx_p, avg_pl])

    def _throughput_reward(self):
        """Sum throughput over UEs minus power penalty."""
        f = 3.5e9
        tx_nodes = [self.twin.network.get_node_by_id(t) for t in self.tx_ids]
        ue_nodes = [self.twin.network.get_node_by_id(u) for u in self.ue_ids]
        tx_xyz = np.array([n.position for n in tx_nodes], float)
        ue_xyz = np.array([n.position for n in ue_nodes], float)
        tx_p_dbm = np.array([n.transceiver_properties.transmit_power_dbm for n in tx_nodes], float)
        g_db = np.zeros_like(tx_p_dbm)
        ant_losses_db = np.zeros_like(tx_p_dbm)
        pl_db = fspl_matrix_db(tx_xyz, ue_xyz, f)          # (T,U)
        rsrp_dbm = rsrp_matrix_dbm(tx_p_dbm, g_db, ant_losses_db, pl_db)  # (T,U)
        noise_dbm = noise_dbm_vector(self.B, noise_figure_db=7.0) * np.ones(ue_xyz.shape[0])
        # best server per UE = argmax over T
        best = np.argmax(rsrp_dbm, axis=0)
        # sinr for each UE served by its best TX
        sinr_db = sinr_db_from_rsrp_matrix(rsrp_dbm, best, noise_dbm)
        thr = shannon_throughput_bps_vector(self.B, sinr_db, self.eta)
        # reward = sum throughput (Gbps) - lambda * sum power (W proxy)
        reward = float(thr.sum() / 1e9) - self.lmb * float(np.sum(10**(tx_p_dbm/10)/1000.0))
        return reward, {"sum_thr_bps": float(thr.sum()), "mean_sinr_db": float(np.mean(sinr_db))}
