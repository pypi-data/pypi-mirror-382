
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
from ..core.node import WirelessNode

@dataclass
class ConstantVelocity:
    velocity_mps: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    start_time: float = 0.0
    _last_t: Optional[float] = None
    def update(self, node: WirelessNode, timestamp: float) -> None:
        if self._last_t is None:
            self._last_t = timestamp
            return
        dt = max(0.0, timestamp - self._last_t)
        self._last_t = timestamp
        x, y, z = node.position
        vx, vy, vz = self.velocity_mps
        node.move_to((x + vx * dt, y + vy * dt, z + vz * dt))

class ConstantVelocityMobility:
    """Back-compat wrapper over ConstantVelocity."""
    def __init__(self, dimensions=(1000,1000), velocity_mps=5.0, **_):
        if isinstance(velocity_mps, (int, float)):
            vel = (float(velocity_mps), 0.0, 0.0)
        else:
            vel = tuple(velocity_mps) + (0.0,)
            vel = vel[:3]
        self.impl = ConstantVelocity(velocity_mps=vel)
        self.dim = dimensions
        self.path_history = []

    def update(self, pos, dt):
        new_pos = self.impl.step((pos[0], pos[1], pos[2] if len(pos) > 2 else 0.0), dt)
        self.path_history.append((new_pos[0], new_pos[1]))
        # clamp to bounds
        x = max(0, min(self.dim[0], new_pos[0]))
        y = max(0, min(self.dim[1], new_pos[1]))
        z = new_pos[2] if len(new_pos) > 2 else 0.0
        return (x, y, z)

