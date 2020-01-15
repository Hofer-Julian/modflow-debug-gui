from pathlib import Path
import matplotlib.pyplot as plt

import flopy
from utils import plot_model

sim_name = "mfsim.nam"
modflow_path = Path("c:/checkouts/modflow6/bin/mf6d.exe")
sim_path = Path("c:/checkouts/modflow-debug-gui/data/ex_10x10_transient")

sim = flopy.mf6.MFSimulation.load(
    sim_name=sim_name, version="mf6", exe_name=str(modflow_path), sim_ws=str(sim_path)
)

sim.run_simulation()

plot_model(sim, sim_path, layer=0, display_text=False)
plt.show()
