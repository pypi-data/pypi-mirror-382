from __future__ import annotations
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from pytwinnet.accelerate.vectorized import fspl_matrix_db, rsrp_matrix_dbm, noise_dbm_vector, sinr_db_from_rsrp_matrix

def _sinr_grid(twin, tx_id: str, xlim=(0,400), ylim=(0,400), res=100):
    f = 3.5e9
    xs = np.linspace(*xlim, res)
    ys = np.linspace(*ylim, res)
    XX, YY = np.meshgrid(xs, ys)
    test_xyz = np.stack([XX.ravel(), YY.ravel(), np.zeros_like(XX).ravel()+1.5], axis=1)

    tx_nodes = [twin.network.get_node_by_id(tx_id)]
    interferers = [n for n in twin.network if n.metadata.get("role") == "gNB" and n.node_id != tx_id]
    tx_all = tx_nodes + interferers
    tx_xyz = np.array([n.position for n in tx_all], float)
    p_dbm = np.array([n.transceiver_properties.transmit_power_dbm for n in tx_all], float)
    g_db = np.zeros_like(p_dbm)
    pl = fspl_matrix_db(tx_xyz, test_xyz, f)
    rsrp = rsrp_matrix_dbm(p_dbm, g_db, np.zeros_like(p_dbm), pl)
    best = np.array([0]*test_xyz.shape[0])  # force serving by selected tx
    noise = noise_dbm_vector(20e6, 7.0) * np.ones(test_xyz.shape[0])
    sinr = sinr_db_from_rsrp_matrix(rsrp, best, noise).reshape(res, res)
    return xs, ys, sinr

def main(twin):
    st.set_page_config(page_title="PyTwinNet Dashboard", layout="wide")
    st.sidebar.title("PyTwinNet Dashboard")
    txs = [n.node_id for n in twin.network if n.metadata.get("role") == "gNB"]
    tx_id = st.sidebar.selectbox("Serving gNB", options=txs, index=0 if txs else None)
    res = st.sidebar.slider("Resolution", 50, 400, 150, 50)
    pr = st.sidebar.slider("Power (dBm)", 10, 40, 32)
    if tx_id:
        n = twin.network.get_node_by_id(tx_id)
        n.transceiver_properties.transmit_power_dbm = float(pr)

    st.header("Downlink SINR Heatmap")
    if tx_id:
        xs, ys, Z = _sinr_grid(twin, tx_id, (0, 400), (0, 400), res)
        fig = go.Figure(data=go.Heatmap(x=xs, y=ys, z=Z, colorbar=dict(title="SINR(dB)")))
        fig.update_layout(xaxis_title="X (m)", yaxis_title="Y (m)", margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.header("Nodes")
    for n in twin.network:
        st.write(f"{n.node_id}: pos={n.position}, tx={getattr(n.transceiver_properties, 'transmit_power_dbm', 'N/A')} dBm")
