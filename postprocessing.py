import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from lib import init
from skgeom.draw import draw
from constants import MTOMM
from matplotlib import cm
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_trajectories(traj, geo, filename=None):
    x = traj[traj.step == traj.step.max()].x
    y = traj[traj.step == traj.step.max()].y

    plt.figure(figsize=(10, 3), dpi=300)
    plt.scatter(x, y, s=0.5)

    for ped_id in traj.id.unique():
        df = traj.loc[traj['id'] == ped_id]
        df = df.sort_values('step')
        plt.plot(df.x, df.y, linewidth=0.3, alpha=0.5)

    draw(geo.floor, alpha=0.2)

    plt.axis('equal')
    plt.gca().set_adjustable("box")

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')


def plot_histogram(traj, geo, filename=None):
    x = traj[traj.step == traj.step.max()].x
    y = traj[traj.step == traj.step.max()].y

    fig, axScatter = plt.subplots(figsize=(10, 5), dpi=300)

    # the scatter plot:
    axScatter.scatter(x, y, s=0.5)
    axScatter.set_aspect(1.)
    draw(geo.floor, alpha=0.2)

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

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')


def plot_space_usage(traj, geometry, grid, filename=None):
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
    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage, cmap=cm.coolwarm, shading='auto')

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    plt.colorbar(orientation="horizontal")

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')


file = open('geometries/platform.xml', 'r')
geometry, grid = init(file)

directory = r'results-change-weight'
output_path = r'results-change-weight-plots'

if not os.path.exists(os.path.join(output_path, 'traj')):
    os.makedirs(os.path.join(output_path, 'traj'))
if not os.path.exists(os.path.join(output_path, 'hist')):
    os.makedirs(os.path.join(output_path, 'hist'))

if not os.path.exists(os.path.join(output_path, 'spus')):
    os.makedirs(os.path.join(output_path, 'spus'))

i = 0
for subdir in os.scandir(directory):
    if i > 10:
        break

    if os.path.isdir(subdir):
        print('processing: {}'.format(os.path.join(subdir, 'traj.csv')))
        if os.path.exists(os.path.join(subdir, 'traj.csv')):
            traj = pd.read_csv(os.path.join(subdir, 'traj.csv'))
            traj = traj.loc[traj.step < 200]
            suffix = subdir.name

            traj_filename = 'traj/traj_{}.pdf'.format(suffix)
            traj_outputpath = os.path.join(output_path, traj_filename)
            plot_trajectories(traj, geometry, traj_outputpath)


            hist_filename = 'hist/hist_{}.pdf'.format(suffix)
            hist_outputpath = os.path.join(output_path, hist_filename)
            plot_histogram(traj, geometry, hist_outputpath)

            spus_filename = 'spus/spus_{}.pdf'.format(suffix)
            spus_outputpath = os.path.join(output_path, spus_filename)
            plot_space_usage(traj, geometry, grid, spus_outputpath)
            i = i + 1

        else:
            print('trajectory does not exist')


# traj =  pd.read_csv('data/traj.csv')
# traj = pd.read_csv('results/traj-test/traj.csv')
#
# plot_trajectories(traj, geometry)
# plot_histogram(traj, geometry)
# plot_space_usage(traj, geometry, grid)
