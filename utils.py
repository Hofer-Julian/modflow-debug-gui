import numpy as np
from matplotlib import pyplot as plt
import flopy


def plot_model(sim, sim_path, layer):

    fig, ax = plt.subplots()
    fig.set_size_inches(5, 10)

    models = []
    headobjects = []
    times = None
    plotarrays = []
    xgrids = []
    ygrids = []
    vmin = np.inf
    vmax = -np.inf

    for i, model_name in enumerate(list(sim.model_names)):
        models.append(sim.get_model(model_name))

        hds_name = sim_path / (model_name + ".hds")
        headobjects.append(flopy.utils.HeadFile(hds_name, model=models[i]))

        times = headobjects[i].get_times()

        # Get heads of layer at end of simulation (times[-1])
        plotarray = headobjects[i].get_data(totim=times[-1])[layer, :, :]

        # Mask cells having the HDRY (1e+30) value
        plotarrays.append(np.ma.masked_equal(plotarray, [1e30]))

        xgrids.append(np.array(models[i].modelgrid.xvertices))
        ygrids.append(np.array(models[i].modelgrid.yvertices))

        local_min = np.min(plotarrays[i])
        if local_min < vmin:
            vmin = local_min

        local_max = np.max(plotarrays[i])
        if local_max > vmax:
            vmax = local_max

    for i in range(len(plotarrays)):

        cm = ax.pcolormesh(xgrids[i], ygrids[i], plotarrays[i], vmin=vmin, vmax=vmax)

        for j in range(len(plotarrays[i][:, 0])):
            for k in range(len((plotarrays[i][0, :]))):
                if plotarrays[i][j, k] != 0.0:
                    text = plt.text(
                        (xgrids[i][j, k] + xgrids[i][j + 1, k + 1]) / 2,
                        (ygrids[i][j, k] + ygrids[i][j + 1, k + 1]) / 2,
                        f"{plotarrays[i][j, k]:02.0}",
                        ha="center",
                        va="center",
                        color="w",
                        fontsize=8,
                    )

    fig.colorbar(cm, ax=ax)

