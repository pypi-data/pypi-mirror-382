"""Signal utilities for examples: noise power, SINR, Shannon capacity."""
import numpy as np

def calculate_noise_power(bw_hz: float, noise_figure_db: float = 7.0) -> float:
    kT_dbm_per_hz = -174.0
    return kT_dbm_per_hz + 10*np.log10(bw_hz) + noise_figure_db  # dBm

def calculate_sinr_db(signal_dbm: float, interference_dbm_list, noise_dbm: float) -> float:
    def dbm2mw(x): return 10**(x/10.0)
    s = dbm2mw(signal_dbm)
    i = sum(dbm2mw(v) for v in (interference_dbm_list or []))
    n = dbm2mw(noise_dbm)
    return 10*np.log10(s / (i + n + 1e-30) + 1e-30)

def shannon_capacity(sinr_db: float, bw_hz: float, efficiency: float = 0.75) -> float:
    sinr = 10**(sinr_db/10.0)
    return efficiency * bw_hz * np.log2(1.0 + sinr)  # bps
