from utils import get_bmi_data
from pathlib import Path
import os

dllpath = Path("c:/checkouts/modflow6-martijn-fork/msvs/dll/x64/Debug/mf6.dll")
simpath = Path("c:/checkouts/modflow-debug-gui/data/test120_mv_dis-lgr_3models")

os.chdir(simpath)

# var_names = [b"MV NPF/K11", b"MV NPF/K33", b"MV NPF/IK33", b"MV NPF/SAT"]
var_names = [b"MV NPF/K11", b"MV NPF/K33", b"MV NPF/SAT"]

get_bmi_data(str(dllpath), var_names)
