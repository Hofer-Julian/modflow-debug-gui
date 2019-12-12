import numpy as np
import ctypes
from collections import defaultdict
from matplotlib import pyplot as plt


def get_bmi_data(dllpath, var_names):

    print("running from mf6 dll: ", dllpath)
    mf6 = ctypes.cdll.LoadLibrary(dllpath)

    # initialize the model
    mf6.initialize()

    # get times
    ct = ctypes.c_double(0.0)
    mf6.get_current_time(ctypes.byref(ct))
    et = ctypes.c_double(0.0)
    mf6.get_end_time(ctypes.byref(et))

    # acessing exported value from dll
    maxstrlen = ctypes.c_int.in_dll(mf6, "MAXSTRLEN").value

    # TODO_JH: Change b"TESTJE NPF/K11" to something general
    c_var_name = ctypes.c_char_p(b"TESTJE NPF/K11")
    grid_id = ctypes.c_int(0)
    mf6.get_var_grid(c_var_name, ctypes.byref(grid_id))
    print(f"grid id: {grid_id.value}")

    # get grid type
    grid_type = ctypes.create_string_buffer(maxstrlen)
    mf6.get_grid_type(ctypes.byref(grid_id), grid_type)
    print(f"grid type: {grid_type.value.decode('ASCII')}")

    # get grid rank
    grid_rank = ctypes.c_int(0)
    mf6.get_grid_rank(ctypes.byref(grid_id), ctypes.byref(grid_rank))
    grid_rank = grid_rank.value
    print(f"grid rank: {grid_rank}")

    # get grid size
    grid_size = ctypes.c_int(0)
    mf6.get_grid_size(ctypes.byref(grid_id), ctypes.byref(grid_size))
    grid_size = grid_size.value
    print(f"grid size: {grid_size}")

    # get grid shape
    grid_shape = np.ctypeslib.ndpointer(
        dtype="int", ndim=1, shape=(grid_rank,), flags="F"
    )()
    mf6.get_grid_shape(ctypes.byref(grid_id), ctypes.byref(grid_shape))
    grid_shape = grid_shape.contents
    print(f"grid shape: {grid_shape}")

    # get grid x
    grid_x = np.ctypeslib.ndpointer(
        dtype="double", ndim=1, shape=(grid_shape[-1],), flags="F"
    )()
    mf6.get_grid_x(ctypes.byref(grid_id), ctypes.byref(grid_x))
    grid_x = grid_x.contents
    print(f"grid x: {grid_x}")

    # get grid y
    grid_y = np.ctypeslib.ndpointer(
        dtype="double", ndim=1, shape=(grid_shape[-2],), flags="F"
    )()
    mf6.get_grid_y(ctypes.byref(grid_id), ctypes.byref(grid_y))
    grid_y = grid_y.contents
    print(f"grid y: {grid_y}")

    # get grid z would be grid_shape.contents[-3]

    # initialize dictionary
    var_dict = defaultdict(dict)
    for key in var_names:
        # get variable size(s)
        elsize = ctypes.c_int(0)
        nbytes = ctypes.c_int(0)
        var_dict[key]["name"] = ctypes.c_char_p(key)

        mf6.get_var_itemsize(var_dict[key]["name"], ctypes.byref(elsize))
        mf6.get_var_nbytes(var_dict[key]["name"], ctypes.byref(nbytes))
        nsize = int(nbytes.value / elsize.value)

        var_dict[key]["type"] = var_names[key]

        # declare the receiving pointers-to-array
        var_dict[key]["array"] = np.ctypeslib.ndpointer(
            dtype=var_dict[key]["type"], ndim=1, shape=(nsize,), flags="F"
        )()
    # model time loop
    while ct.value < et.value:
        # calculate
        mf6.update()
        # update time
        mf6.get_current_time(ctypes.byref(ct))

        for key in var_names:
            # get data
            if var_dict[key]["type"] == "double":
                mf6.get_value_ptr_double(
                    var_dict[key]["name"], ctypes.byref(var_dict[key]["array"])
                )
            elif var_dict[key]["type"] == "int":
                mf6.get_value_ptr_int(
                    var_dict[key]["name"], ctypes.byref(var_dict[key]["array"])
                )

            vararray = var_dict[key]["array"].contents

            if key == b"SLN_1/X":

                print(f"grid x: {grid_x}")
                # TODO: Check if "A" is the right option to use
                plt.pcolormesh(grid_x, grid_y, vararray.reshape(grid_shape, order="A"))
                plt.colorbar()
                plt.show()

    # cleanup
    mf6.finalize()
