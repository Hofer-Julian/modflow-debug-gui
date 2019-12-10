from utils import get_bmi_data
from pathlib import Path
import os

dllpath = Path("c:/checkouts/modflow6-martijn-fork/msvs/dll/x64/Debug/mf6.dll")
simpath = Path("c:/checkouts/modflow-debug-gui/data/ex_10x10")

os.chdir(simpath)


# TODO_JH: Find a way to convert "SLN_1/X" -> "testje SLN_1/X"
# without breaking functionality

# Everything needs to be uppercase!
var_names = [b"SLN_1/X"]
var_names = [
    b"TESTJE NPF/K11",
    b"TESTJE NPF/K33",
    b"TESTJE NPF/SAT",
    b"TESTJE NPF/ICELLTYPE",
]

get_bmi_data(str(dllpath), var_names)
