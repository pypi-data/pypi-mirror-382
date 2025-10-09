
from __future__ import annotations
import math
import numpy as np
from abc import ABC, abstractmethod
from ..core.node import WirelessNode
from .environment import Environment

class PropagationModel(ABC):
    @abstractmethod
    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float: ...

class FreeSpacePathLoss(PropagationModel):
    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float:
        dx = tx.position[0] - rx.position[0]
        dy = tx.position[1] - rx.position[1]
        dz = tx.position[2] - rx.position[2]
        d_m = math.sqrt(dx*dx + dy*dy + dz*dz)
        d_km = max(d_m, 1e-3) / 1000.0
        f_mhz = max(tx.transceiver_properties.carrier_frequency_hz, 1.0) / 1e6
        return 20.0 * math.log10(d_km) + 20.0 * math.log10(f_mhz) + 32.44
    
    
    def faded_shadowed_model(d: float, freq_ghz: float, tx_power_dbm: float,
                            n: float = 2.0, sigma: float = 6.0) -> float:
        """Log-distance with lognormal shadowing + Rayleigh fading; returns Rx power (dBm)."""
        f_hz = freq_ghz * 1e9
        # FSPL baseline 
        fspl = FreeSpacePathLoss().calculate_path_loss_scalar(d, f_hz) \
            if hasattr(FreeSpacePathLoss(), "calculate_path_loss_scalar") \
            else FreeSpacePathLoss()._path_loss_scalar(d, f_hz)
        # Log-distance tweak
        ref1 = FreeSpacePathLoss()._path_loss_scalar(1.0, f_hz)
        pl_db = ref1 + 10*n*np.log10(max(d, 1e-3))
        # Shadowing + fading
        shadow = np.random.normal(0.0, sigma)
        ray = np.random.rayleigh(1.0)
        fading_db = 20*np.log10(ray + 1e-12)
        path_loss = 0.5*(fspl + pl_db) + shadow - fading_db
        return tx_power_dbm - path_loss

