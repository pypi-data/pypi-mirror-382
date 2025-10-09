"""Compatibility shim for older examples: Transceiver -> TransceiverProperties."""
from dataclasses import dataclass
from typing import Optional
from .node import TransceiverProperties  # existing dataclass

@dataclass
class Transceiver:
    """Back-compat wrapper mapping to TransceiverProperties."""
    tx_power_dbm: float
    frequency_ghz: float
    antenna_gain_dbi: float = 0.0
    rx_noise_figure_db: float = 7.0
    meta: Optional[dict] = None

    def to_properties(self) -> TransceiverProperties:
        return TransceiverProperties(
            transmit_power_dbm=self.tx_power_dbm,
            antenna_gain_dbi=self.antenna_gain_dbi,
            center_frequency_hz=self.frequency_ghz * 1e9,
            noise_figure_db=self.rx_noise_figure_db,
            metadata=self.meta or {},
        )
