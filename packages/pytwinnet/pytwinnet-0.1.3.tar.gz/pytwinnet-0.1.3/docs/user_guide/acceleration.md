
```markdown
# Acceleration (Numba)

Large grids (e.g., SINR heatmaps) benefit from JIT. Enable Numba with:
```
```bash
pip install "pytwinnet[accel]"
```
# Example
```python
from pytwinnet.accel.numba_kernels import fspl_matrix_db_numba
pl = fspl_matrix_db_numba(tx_xyz, rx_xyz, 3.5e9)
```