from utils import get_bmi_data
from pathlib import Path
import os

dllpath = Path("c:/checkouts/modflow6-martijn-fork/msvs/dll/x64/Debug/mf6.dll")
simpath = Path("c:/checkouts/modflow-debug-gui/data/ex_10x10")

os.chdir(simpath)

# var_names = [b"MV NPF/K11", b"MV NPF/K33", b"MV NPF/SAT"]
var_names = [b"SLN_1/X"]

get_bmi_data(str(dllpath), var_names)
