from pytwinnet.rl import PowerControlEnv
from pytwinnet.core import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
import numpy as np

twin = DigitalTwin()
twin.set_environment(Environment(dimensions_m=(400,400,30)))
twin.set_propagation_model(FreeSpacePathLoss())
net = Network()
net.add_node(WirelessNode("gNB-1",(100,100,10),TransceiverProperties(30,5),metadata={"role":"gNB"}))
net.add_node(WirelessNode("gNB-2",(300,300,10),TransceiverProperties(30,5),metadata={"role":"gNB"}))
for i in range(5):
    net.add_node(WirelessNode(f"UE-{i+1}",(50+60*i, 150, 1.5)))
twin.network = net

env = PowerControlEnv(twin, tx_ids=["gNB-1","gNB-2"], ue_ids=[f"UE-{i+1}" for i in range(5)], penalty_lambda=0.0)
obs = env.reset()
for t in range(10):
    act = np.random.choice([-1,0,1], size=2)  # random policy demo
    obs, r, term, trunc, info = env.step(act)
    print(f"t={t} act={act} reward={r:.3f} info={info}")
