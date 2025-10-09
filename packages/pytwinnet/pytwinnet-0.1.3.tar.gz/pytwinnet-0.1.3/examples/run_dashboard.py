import streamlit.web.bootstrap as boot
from pytwinnet.core import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.dashboard.streamlit_app import main

twin = DigitalTwin()
twin.set_environment(Environment(dimensions_m=(400,400,30)))
twin.set_propagation_model(FreeSpacePathLoss())
net = Network()
net.add_node(WirelessNode("gNB-1",(100,100,10),TransceiverProperties(32,5),metadata={"role":"gNB"}))
net.add_node(WirelessNode("gNB-2",(300,300,10),TransceiverProperties(32,5),metadata={"role":"gNB"}))
twin.network = net

# streamlit needs a callable; wrap lambda to capture twin
def _app():
    main(twin)
boot.run("_app", "", [], {})

# You can use on arduino
# streamlit run examples/run_dashboard.py

