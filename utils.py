import numpy as np
from matplotlib import pyplot as plt
import flopy
import re
import matplotlib.patches as mpatches
import ctypes
from collections import defaultdict


def plot_model(sim, sim_path, layer):

    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)

    models = {}
    headobjects = {}
    times = None
    plotarrays = {}
    xgrids = {}
    ygrids = {}
    vmin = np.inf
    vmax = -np.inf
    xmin = np.inf
    xmax = -np.inf
    ymin = np.inf
    ymax = -np.inf

    for model_name in list(sim.model_names):
        models.update({model_name: sim.get_model(model_name)})

        hds_name = sim_path / (model_name + ".hds")
        headobjects.update(
            {model_name: flopy.utils.HeadFile(hds_name, model=models[model_name])}
        )

        times = headobjects[model_name].get_times()

        # Get heads of layer at end of simulation (times[-1])
        plotarray = headobjects[model_name].get_data(totim=times[-1])[layer, :, :]

        # Mask cells having the HDRY (1e+30) value
        plotarrays.update({model_name: np.ma.masked_equal(plotarray, [1e30])})

        xgrids.update({model_name: np.array(models[model_name].modelgrid.xvertices)})
        ygrids.update({model_name: np.array(models[model_name].modelgrid.yvertices)})

        # Determine suitable plot ranges
        local_vmin = np.min(plotarrays[model_name])
        if local_vmin < vmin:
            vmin = local_vmin

        local_vmax = np.max(plotarrays[model_name])
        if local_vmax > vmax:
            vmax = local_vmax

        local_xmin = np.min(xgrids[model_name])
        if local_xmin < xmin:
            xmin = local_xmin

        local_xmax = np.max(xgrids[model_name])
        if local_xmax > xmax:
            xmax = local_xmax

        local_ymin = np.min(ygrids[model_name])
        if local_ymin < ymin:
            ymin = local_ymin

        local_ymax = np.max(ygrids[model_name])
        if local_ymax > ymax:
            ymax = local_ymax

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    for model_name in list(sim.model_names):

        cm = ax.pcolormesh(
            xgrids[model_name],
            ygrids[model_name],
            plotarrays[model_name],
            vmin=vmin,
            vmax=vmax,
        )

        # Text rendering is a performance problem.
        # Among other things, because it renders outside plotrange
        # which can be made visible by changing fontcolor
        for j in range(len(plotarrays[model_name][:, 0])):
            for k in range(len((plotarrays[model_name][0, :]))):
                if plotarrays[model_name][j, k] != 0.0:
                    text = ax.text(
                        (xgrids[model_name][j, k] + xgrids[model_name][j + 1, k + 1])
                        / 2,
                        (ygrids[model_name][j, k] + ygrids[model_name][j + 1, k + 1])
                        / 2,
                        f"{plotarrays[model_name][j, k]:02.0}",
                        ha="center",
                        va="center",
                        color="white",
                        fontsize=8,
                    )

    def plot_arrow(ax, model_name_1, model_name_2, row_1, column_1, row_2, column_2):
        x_middlepoint_1 = (
            xgrids[model_name_1][row_1 - 1, column_1 - 1]
            + xgrids[model_name_1][row_1, column_1]
        ) / 2
        y_middlepoint_1 = (
            ygrids[model_name_1][row_1 - 1, column_1 - 1]
            + ygrids[model_name_1][row_1, column_1]
        ) / 2
        x_middlepoint_2 = (
            xgrids[model_name_2][row_2 - 1, column_2 - 1]
            + xgrids[model_name_2][row_2, column_2]
        ) / 2
        y_middlepoint_2 = (
            ygrids[model_name_2][row_2 - 1, column_2 - 1]
            + ygrids[model_name_2][row_2, column_2]
        ) / 2

        arrow = mpatches.FancyArrowPatch(
            (x_middlepoint_1, y_middlepoint_1),
            (x_middlepoint_2, y_middlepoint_2),
            mutation_scale=20,
        )
        ax.add_patch(arrow)

    exchangedata_files = sim.simulation_data.mfdata[
        "nam", "exchanges", "exchanges"
    ].get_data()

    for file_data in exchangedata_files:
        with open(sim_path / file_data[1], "r") as exchangefile:
            exchangedata_block = False
            for line in exchangefile:
                if line == "BEGIN exchangedata":
                    exchangedata_block = True
                if line == "END exchangedata":
                    exchangedata_block = False

                if exchangedata_block:
                    match = re.search(r"(\d+) (\d+) (\d+)  (\d+) (\d+) (\d+)", line)
                    if match:
                        if (
                            int(match.group(1)) == layer + 1
                            and int(match.group(4)) == layer + 1
                        ):
                            plot_arrow(
                                ax,
                                file_data[2],
                                file_data[3],
                                int(match.group(2)),
                                int(match.group(3)),
                                int(match.group(5)),
                                int(match.group(6)),
                            )

    fig.colorbar(cm, ax=ax)


def get_bmi_data(dllpath, keys):
    print("running from mf6 dll: ", dllpath)
    mf6 = ctypes.cdll.LoadLibrary(dllpath)

    # initialize the model
    mf6.initialize()

    # get times
    ct = ctypes.c_double(0.0)
    mf6.get_current_time(ctypes.byref(ct))
    et = ctypes.c_double(0.0)
    mf6.get_end_time(ctypes.byref(et))

    # acessing exported values from dll
    maxstrlen = ctypes.c_int.in_dll(mf6, "MAXSTRLEN")

    grid_id = ctypes.c_int(0)

    # get grid type
    grid_type = ctypes.create_string_buffer(maxstrlen.value)
    mf6.get_grid_type(grid_id, grid_type)
    print(f"grid type: {grid_type.value.decode('ASCII')}")

    # get grid rank
    grid_rank = ctypes.c_int(0)
    mf6.get_grid_rank(grid_id, ctypes.byref(grid_rank))
    print(f"grid rank: {grid_rank.value}")

    # get grid size
    grid_size = ctypes.c_int(0)
    mf6.get_grid_size(grid_id, ctypes.byref(grid_size))
    print(f"grid size: {grid_size.value}")

    # get grid shape
    grid_shape = np.ctypeslib.ndpointer(
        dtype="int", ndim=1, shape=(grid_rank.value,), flags="F"
    )()
    mf6.get_grid_shape(
        grid_id, ctypes.byref(grid_shape)
    )
    print(f"grid shape: {grid_shape.contents}")

    # get grid x
    grid_x = np.ctypeslib.ndpointer(
        dtype="int", ndim=1, shape=(grid_shape.contents[-1],), flags="F"
    )()
    mf6.get_grid_x(
        grid_id, ctypes.byref(grid_x)
    )
    print(f"grid x: {grid_x.contents}")

    # get grid y
    grid_y = np.ctypeslib.ndpointer(
        dtype="int", ndim=1, shape=(grid_shape.contents[-2],), flags="F"
    )()
    mf6.get_grid_y(
        grid_id, ctypes.byref(grid_y)
    )
    print(f"grid y: {grid_y.contents}")

    # get grid z would be grid_shape.contents[-3]

    

    # initialize dictionary
    var_dict = defaultdict(dict)

    for key in keys:
        # get variable size(s)PliP
        elsize = ctypes.c_int(0)
        nbytes = ctypes.c_int(0)
        var_dict[key]["name"] = ctypes.c_char_p(key)

        mf6.get_var_itemsize(var_dict[key]["name"], ctypes.byref(elsize))
        mf6.get_var_nbytes(var_dict[key]["name"], ctypes.byref(nbytes))
        nsize = int(nbytes.value / elsize.value)


        # declare the receiving pointers-to-array
        var_dict[key]["array"] = np.ctypeslib.ndpointer(
            dtype="double", ndim=1, shape=(nsize,), flags="F"
        )()

    # model time loop
    while ct.value < et.value:
        # calculate
        mf6.update()

        # update time
        mf6.get_current_time(ctypes.byref(ct))

        for key in keys:
            # get data
            mf6.get_value_ptr_double(
                var_dict[key]["name"], ctypes.byref(var_dict[key]["array"])
            )
            vararray = var_dict[key]["array"].contents
            print(key.decode("ASCII"), vararray)

    # cleanup
    mf6.finalize()

