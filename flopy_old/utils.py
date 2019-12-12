import numpy as np
import re
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import flopy


def plot_model(sim, sim_path, layer, display_text=True):

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
        if display_text:
            # Text rendering is a performance problem.
            # Among other things, because it renders outside plotrange
            # which can be made visible by changing fontcolor
            for j in range(len(plotarrays[model_name][:, 0])):
                for k in range(len((plotarrays[model_name][0, :]))):
                    if plotarrays[model_name][j, k] != 0.0:
                        ax.text(
                            (
                                xgrids[model_name][j, k]
                                + xgrids[model_name][j + 1, k + 1]
                            )
                            / 2,
                            (
                                ygrids[model_name][j, k]
                                + ygrids[model_name][j + 1, k + 1]
                            )
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
    if exchangedata_files:
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
