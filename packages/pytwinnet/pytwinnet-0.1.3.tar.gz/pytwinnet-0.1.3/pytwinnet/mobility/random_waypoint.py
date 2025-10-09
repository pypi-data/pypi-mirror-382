
from __future__ import annotations
import random, math
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from ..core.node import WirelessNode
from ..physics.environment import Environment

@dataclass
class RandomWaypoint:
    env: Environment
    speed_range_mps: Tuple[float, float] = (0.5, 1.5)
    pause_time_s: float = 0.0
    seed: int = 0
    _rng: random.Random = None
    _target: Optional[Tuple[float, float, float]] = None
    _speed: float = 0.0
    _paused_until: float = 0.0
    _last_t: Optional[float] = None
    def __post_init__(self):
        self._rng = random.Random(self.seed)
    def _sample_waypoint(self) -> Tuple[float, float, float]:
        w, d, h = self.env.dimensions_m
        return (self._rng.uniform(0, w), self._rng.uniform(0, d), self._rng.uniform(0, h))
    def update(self, node: WirelessNode, timestamp: float) -> None:
        if self._last_t is None:
            self._last_t = timestamp
            self._target = self._sample_waypoint()
            self._speed = self._rng.uniform(*self.speed_range_mps)
            return
        dt = max(0.0, timestamp - self._last_t)
        self._last_t = timestamp
        if timestamp < self._paused_until:
            return
        x, y, z = node.position
        tx, ty, tz = self._target
        dx, dy, dz = tx - x, ty - y, tz - z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 1e-6:
            self._paused_until = timestamp + self.pause_time_s
            self._target = self._sample_waypoint()
            self._speed = self._rng.uniform(*self.speed_range_mps)
            return
        step = self._speed * dt
        if step >= dist:
            node.move_to((tx, ty, tz))
        else:
            nx = x + dx / dist * step
            ny = y + dy / dist * step
            nz = z + dz / dist * step
            node.move_to((nx, ny, nz))

# --------------------------------------------------------------------------
# Backwards-compatibility adapter for legacy examples
# --------------------------------------------------------------------------

class RandomWaypointMobility:
    """
    Simplified random waypoint model compatible with old examples.
    It does not require a WirelessNode or Environment object.
    """
    def __init__(self, dimensions=(1000,1000), velocity_mps=(1,10), wait_time_s=(0,5), seed=None, **_):
        self.W, self.H = dimensions
        self.vmin, self.vmax = velocity_mps
        self.wmin, self.wmax = wait_time_s
        self.rng = np.random.default_rng(seed)
        self.path_history = []
        self._target = None
        self._wait = 0.0
        self._speed = None

    def _choose_target(self, x, y):
        self._target = (self.rng.uniform(0,self.W), self.rng.uniform(0,self.H))
        self._speed = self.rng.uniform(self.vmin, self.vmax)
        self._wait = self.rng.uniform(self.wmin, self.wmax)

    def update(self, pos, dt):
        x,y,*_ = pos
        if self._target is None:
            self._choose_target(x,y)
        if self._wait > 0:
            self._wait = max(0.0, self._wait - dt)
            self.path_history.append((x,y))
            return (x,y, pos[2] if len(pos)>2 else 0.0)

        tx,ty = self._target
        dx, dy = tx - x, ty - y
        d = np.hypot(dx, dy)
        if d < 1e-6:
            self._choose_target(x,y)
            self.path_history.append((x,y))
            return (x,y, pos[2] if len(pos)>2 else 0.0)

        step = self._speed * dt
        if step >= d:
            x,y = tx,ty
            self._choose_target(x,y)
        else:
            x += dx * (step/d)
            y += dy * (step/d)
        self.path_history.append((x,y))
        return (max(0,min(self.W,x)), max(0,min(self.H,y)), pos[2] if len(pos)>2 else 0.0)

