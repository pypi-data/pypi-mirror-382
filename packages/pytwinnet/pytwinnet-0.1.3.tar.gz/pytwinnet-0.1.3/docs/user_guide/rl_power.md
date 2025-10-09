
```markdown
# Reinforcement Learning for Power Control
## Environment
`pytwinnet.rl.PowerControlEnv` is a lightweight, gym-like environment:
- **State**: TX powers + pathloss snapshot to UEs
- **Action**: vector in $\{-1,0,+1\} \times (#TX)$, step size = $\Delta_{dB}$
- **Reward**: sum throughput (Gbps) − $\lambda$ $\cdot$ power penalty
```

## Usage
```python
from pytwinnet.rl import PowerControlEnv
# twin/network prepared elsewhere…
env = PowerControlEnv(
    twin, tx_ids=["gNB-1","gNB-2"], ue_ids=["UE-1","UE-2","UE-3"],
    bandwidth_hz=20e6, efficiency=0.75, power_step_db=1.0, penalty_lambda=0.0
)
obs = env.reset(seed=0)
for t in range(10):
    action = np.random.choice([-1,0,1], size=len(env.tx_ids))
    obs, reward, terminated, truncated, info = env.step(action)
    print(t, reward, info)
```