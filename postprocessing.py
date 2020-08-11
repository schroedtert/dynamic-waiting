import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
from lib import init
import skgeom as sg
from skgeom.draw import draw
from constants import MTOMM
from matplotlib import cm

#
# # definitions for the axes
# left, width = 0.1, 0.65
# bottom, height = 0.1, 0.65
# spacing = 0.005
#
# rect_scatter = [left, bottom, width, height]
# rect_histx = [left, bottom + height + spacing, width, 0.2]
# rect_histy = [left + width + spacing, bottom, 0.2, height]
#
# # start with a square Figure
# fig = plt.figure(figsize=(8, 8))
#
#
# traj =  pd.read_csv('results/platform-test/traj.csv')
# print(traj)
#
# plt.figure()
# plt.title("traj")
#
# x = traj[traj.step == traj.step.max()].x
# y = traj[traj.step == traj.step.max()].y
# plt.hist2d(x, y, bins=300)
# # plt.scatter(x, y, color='black', s=5.5)
#
# # for ped_id in traj.id.unique():
# #     df = traj.loc[traj['id'] == ped_id]
# #     df = df.sort_values('step')
# #     plt.plot(df.x, df.y, alpha=0.5, linewidth=0.2)
#
#
#
# plt.axis('equal')
# plt.gca().set_adjustable("box")
# # plt.xlim([-100000, 30000])
# plt.show()

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_trajectories(traj, geo):
    x = traj[traj.step == traj.step.max()].x
    y = traj[traj.step == traj.step.max()].y

    plt.figure(figsize=(10, 3), dpi=300)
    plt.scatter(x, y, s=0.5)

    for ped_id in traj.id.unique():
        df = traj.loc[traj['id'] == ped_id]
        df = df.sort_values('step')
        plt.plot(df.x, df.y, linewidth=0.2, alpha=0.5)

    draw(geo.floor, alpha=0.1)

    plt.axis('equal')
    plt.gca().set_adjustable("box")

    plt.show()


def plot_histogram(traj, geo):
    x = traj[traj.step == traj.step.max()].x
    y = traj[traj.step == traj.step.max()].y

    fig, axScatter = plt.subplots(figsize=(10, 5), dpi=300)

    # the scatter plot:
    axScatter.scatter(x, y, s=0.5)
    axScatter.set_aspect(1.)
    draw(geo.floor, alpha=0.1)

    # create new axes on the right and on the top of the current axes
    # The first argument of the new_vertical(new_horizontal) method is
    # the height (width) of the axes to be created in inches.
    divider = make_axes_locatable(axScatter)
    axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)
    axHisty = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)

    # make some labels invisible
    axHistx.xaxis.set_tick_params(labelbottom=False)
    axHisty.yaxis.set_tick_params(labelleft=False)

    # now determine nice limits by hand:
    binwidth = 1000.
    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    lim = (int(xymax / binwidth) + 1) * binwidth

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x, bins=bins)
    axHisty.hist(y, bins=bins, orientation='horizontal')

    # the xaxis of axHistx and yaxis of axHisty are shared with axScatter,
    # thus there is no need to manually adjust the xlim and ylim of these
    # axis.

    # axHistx.set_yticks([0, 50, 100])
    #
    # axHisty.set_xticks([0, 50, 100])

    plt.ylim([-10000, 10000])
    plt.draw()
    plt.show()


def plot_space_usage(traj, geometry, grid):
    space_usage = np.ones_like(grid.gridX)

    steps = int(traj.step.max())

    for ped_id in traj.id.unique():
        df = traj.loc[traj['id'] == ped_id]
        min_step = int(df.step.min())
        max_step = int(df.step.max())
        for step in range(min_step, max_step + 1):
            df_step = df.loc[df.step == step]
            x = df_step['x'].values[0]
            y = df_step['y'].values[0]
            indices = np.argwhere((grid.gridX == x) & (grid.gridY == y))[0]
            space_usage[indices[0], indices[1]] = space_usage[indices[0], indices[1]] + 1

    space_usage = space_usage / steps
    outside = grid.outside_cells
    space_usage = np.ma.MaskedArray(space_usage, outside == 1)

    plt.figure(figsize=(10, 3), dpi=300)
    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage, cmap=cm.coolwarm)

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    plt.colorbar(orientation="horizontal")
    plt.show()


# traj =  pd.read_csv('data/traj.csv')
traj = pd.read_csv('results/traj-test/traj.csv')
file = open('geometries/platform.xml', 'r')
geometry, grid = init(file)

# plot_trajectories(traj, geometry)
# plot_histogram(traj, geometry)
plot_space_usage(traj, geometry, grid)
