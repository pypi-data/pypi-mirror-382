RL Power Control
======================

.. code-block:: python

   import numpy as np
   from pytwinnet.rl import PowerControlEnv
   # prepare twin/network…
   env = PowerControlEnv(twin, tx_ids=["gNB-1","gNB-2"], ue_ids=["UE-1","UE-2","UE-3"])
   obs = env.reset(seed=0)
   for t in range(10):
       action = np.random.choice([-1,0,1], size=2)
       obs, reward, terminated, truncated, info = env.step(action)
       print(t, reward, info)
