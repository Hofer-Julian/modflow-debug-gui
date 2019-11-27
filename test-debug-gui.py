import os
import sys

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import flopy
from utils import plot_model

sim_name = "mfsim.nam"
modflow_path = Path("c:/checkouts/modflow6/bin/mf6d.exe")
sim_path = Path("c:/checkouts/modflow-debug-gui/data/test120_mv_dis-lgr_3models")

sim = flopy.mf6.MFSimulation.load(
    sim_name=sim_name, version="mf6", exe_name=str(modflow_path), sim_ws=str(sim_path),
)

sim.run_simulation()

plot_model(sim, sim_path, layer=0)
plt.show()
