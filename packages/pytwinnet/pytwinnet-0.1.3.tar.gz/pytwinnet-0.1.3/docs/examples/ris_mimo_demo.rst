
RIS + MIMO Demo
===============

.. code-block:: python

   from pytwinnet.ris import RISPanel, ris_link_gain, phase_opt_greedy
   from pytwinnet.mimo import mimo_rayleigh
   import numpy as np

   N = 64
   h_tr = mimo_rayleigh(nt=N, nr=1)[:,0]
   h_rr = mimo_rayleigh(nt=1, nr=N)[0,:]
   theta = phase_opt_greedy(h_tr, h_rr)
   panel = RISPanel(N); panel.set_phases(theta)
   h_eff = ris_link_gain(h_tr, h_rr, panel.theta)
   print("|h_eff| =", np.abs(h_eff))
