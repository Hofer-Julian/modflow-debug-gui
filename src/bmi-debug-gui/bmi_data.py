from pathlib import Path
import ctypes
import numpy as np
from collections import defaultdict
import os


class BMIState:
    def __init__(self):
        self.dllpath = Path(
            "c:/checkouts/modflow6-martijn-fork/msvs/dll/x64/Debug/mf6.dll"
        )
        self.simpath = Path("c:/checkouts/modflow-debug-gui/data/ex_10x10")
        self.var_names = {b"SLN_1/X": "double"}
        self.mf6 = ctypes.cdll.LoadLibrary(str(self.dllpath))

        os.chdir(self.simpath)

        # initialize the model
        self.mf6.initialize()

        self.ct = ctypes.c_double(0.0)
        self.mf6.get_current_time(ctypes.byref(self.ct))

        self.et = ctypes.c_double(0.0)
        self.mf6.get_end_time(ctypes.byref(self.et))

        # acessing exported value from dll
        self.maxstrlen = ctypes.c_int.in_dll(self.mf6, "MAXSTRLEN").value

        # TODO_JH: Change b"TESTJE NPF/K11" to something general
        c_var_name = ctypes.c_char_p(b"TESTJE NPF/K11")
        self.grid_id = ctypes.c_int(0)
        self.mf6.get_var_grid(c_var_name, ctypes.byref(self.grid_id))
        print(f"grid id: {self.grid_id.value}")

        # get grid type
        self.grid_type = ctypes.create_string_buffer(self.maxstrlen)
        self.mf6.get_grid_type(ctypes.byref(self.grid_id), self.grid_type)
        print(f"grid type: {self.grid_type.value.decode('ASCII')}")

        # get grid rank
        grid_rank = ctypes.c_int(0)
        self.mf6.get_grid_rank(ctypes.byref(self.grid_id), ctypes.byref(grid_rank))
        self.grid_rank = grid_rank.value
        print(f"grid rank: {self.grid_rank}")

        # get grid size
        grid_size = ctypes.c_int(0)
        self.mf6.get_grid_size(ctypes.byref(self.grid_id), ctypes.byref(grid_size))
        self.grid_size = grid_size.value
        print(f"grid size: {self.grid_size}")

        # get grid shape
        grid_shape = np.ctypeslib.ndpointer(
            dtype="int", ndim=1, shape=(self.grid_rank,), flags="F"
        )()
        self.mf6.get_grid_shape(ctypes.byref(self.grid_id), ctypes.byref(grid_shape))
        self.grid_shape = grid_shape.contents
        print(f"grid shape: {self.grid_shape}")

        # get grid x
        grid_x = np.ctypeslib.ndpointer(
            dtype="double", ndim=1, shape=(self.grid_shape[-1],), flags="F"
        )()
        self.mf6.get_grid_x(ctypes.byref(self.grid_id), ctypes.byref(grid_x))
        self.grid_x = grid_x.contents
        print(f"grid x: {self.grid_x}")

        # get grid y
        grid_y = np.ctypeslib.ndpointer(
            dtype="double", ndim=1, shape=(self.grid_shape[-2],), flags="F"
        )()
        self.mf6.get_grid_y(ctypes.byref(self.grid_id), ctypes.byref(grid_y))
        self.grid_y = grid_y.contents
        print(f"grid y: {self.grid_y}")

        # get grid z would be grid_shape.contents[-3]

        # initialize dictionary
        self.var_dict = defaultdict(dict)
        for key in self.var_names:
            # get variable size(s)
            elsize = ctypes.c_int(0)
            nbytes = ctypes.c_int(0)
            self.var_dict[key]["name"] = ctypes.c_char_p(key)

            self.mf6.get_var_itemsize(self.var_dict[key]["name"], ctypes.byref(elsize))
            self.mf6.get_var_nbytes(self.var_dict[key]["name"], ctypes.byref(nbytes))
            nsize = int(nbytes.value / elsize.value)

            self.var_dict[key]["type"] = self.var_names[key]

            # declare the receiving pointers-to-array
            self.var_dict[key]["array"] = np.ctypeslib.ndpointer(
                dtype=self.var_dict[key]["type"], ndim=1, shape=(nsize,), flags="F"
            )()

    def advance_time_loop(self, ax):
        # TODO_JH: implement only one cycle
        # model time loop
        while self.ct.value < self.et.value:
            # calculate
            self.mf6.update()
            # update time
            self.mf6.get_current_time(ctypes.byref(self.ct))

            for key in self.var_names:
                # get data
                if self.var_dict[key]["type"] == "double":
                    self.mf6.get_value_ptr_double(
                        self.var_dict[key]["name"],
                        ctypes.byref(self.var_dict[key]["array"]),
                    )
                elif self.var_dict[key]["type"] == "int":
                    self.mf6.get_value_ptr_int(
                        self.var_dict[key]["name"],
                        ctypes.byref(self.var_dict[key]["array"]),
                    )

                vararray = self.var_dict[key]["array"].contents

                if key == b"SLN_1/X":

                    print(f"grid x: {self.grid_x}")
                    # TODO: Check if "A" is the right option to use
                    ax.pcolormesh(
                        self.grid_x,
                        self.grid_y,
                        vararray.reshape(self.grid_shape, order="A"),
                    )
                    # TODO_JH: Use figure to add colorbar
                    # fig.colorbar()

        # cleanup
        self.mf6.finalize()