import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from lib import init
from skgeom.draw import draw
from constants import MTOMM
from matplotlib import cm
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools
import re

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
    plt.close()


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
    plt.close()

def compute_space_usage(traj, grid):
    space_usage = np.zeros_like(grid.gridX)

    for index, row in traj.iterrows():
        x = row.x
        y = row.y
        indices = grid.get_indices(x, y)
        space_usage[indices[0], indices[1]] = space_usage[indices[0], indices[1]] + 1

    steps = int(traj.step.max())
    outside = grid.outside_cells
    space_usage[outside == 1] = 0
    return space_usage, steps


def plot_space_usage(space_usage, grid, filename=None, title=None):
    plt.figure(figsize=(10, 3), dpi=300)

    if title is not None:
        plt.title(title)

    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage * 100, cmap=cm.jet, vmin=0, vmax=20, shading='auto')

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    # plt.colorbar(orientation="horizontal")
    plt.colorbar()

    plt.gca().set_xlim([-56, 8])

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')
    plt.close()


file = open('geometries/Bern_geo.xml', 'r')
geometry, grid = init(file)

directory = r'/run/media/tobias/Ohne Name/2020-femtc/2020-08-17_real-bern-less-people-stair'
output_path = r'/run/media/tobias/Ohne Name/2020-femtc/2020-08-17_real-bern-plots'

# if not os.path.exists(os.path.join(output_path, 'traj')):
#     os.makedirs(os.path.join(output_path, 'traj'))
# if not os.path.exists(os.path.join(output_path, 'hist')):
#     os.makedirs(os.path.join(output_path, 'hist'))
#
if not os.path.exists(os.path.join(output_path, 'spus')):
    os.makedirs(os.path.join(output_path, 'spus'))
#
# traj = pd.read_csv(os.path.join(directory, 'traj.csv'))
# traj = traj.loc[traj.step < 200]
# suffix = 'test'
#
# traj_filename = 'traj/traj_{}.pdf'.format(suffix)
# traj_outputpath = os.path.join(output_path, traj_filename)
# plot_trajectories(traj, geometry, traj_outputpath)
#
# hist_filename = 'hist/hist_{}.pdf'.format(suffix)
# hist_outputpath = os.path.join(output_path, hist_filename)
# plot_histogram(traj, geometry, hist_outputpath)
#
# spus_filename = 'spus/spus_{}.pdf'.format(suffix)
# spus_outputpath = os.path.join(output_path, spus_filename)
# plot_space_usage(traj, geometry, grid, spus_outputpath)


def process(combination):
    w_exit = combination[0]
    w_wall = combination[1]
    w_door = combination[2]
    w_direction = combination[3]
    reg_string = 'w-exit={:0.2f}_w-wall={:0.2f}_w-door={:0.2f}_w-directions={:1d}'.format(w_exit, w_wall, w_door,
                                                                                          w_direction)
    regex = re.compile('.+_{}_.+'.format(reg_string))

    dirs = []
    for subdir in os.scandir(directory):
        if os.path.isdir(subdir) and re.match(regex, subdir.name):
            if os.path.exists(os.path.join(subdir, 'traj.csv')):
                dirs.append(subdir)
            else:
                print('trajectory does not exist')

    space_usage_all = np.zeros_like(grid.gridX)
    steps_all = 0

    for i in dirs:
        print(i)
    return 

    for subdir in dirs:
        traj = pd.read_csv(os.path.join(subdir, 'traj.csv'))
        suffix = subdir.name

        spus_filename = 'spus/spus_{}.pdf'.format(suffix)
        spus_outputpath = os.path.join(output_path, spus_filename)

        space_usage, steps = compute_space_usage(traj, grid)
        space_usage_all = space_usage_all + space_usage
        steps_all = steps_all + steps

        # traj_filename = 'traj/traj_{}.pdf'.format(suffix)
        # traj_outputpath = os.path.join(output_path, traj_filename)
        # plot_trajectories(traj, geometry)
        # # plot_trajectories(traj, geometry, traj_outputpath)
        #
        # hist_filename = 'hist/hist_{}.pdf'.format(suffix)
        # hist_outputpath = os.path.join(output_path, hist_filename)
        # plot_histogram(traj, geometry)
        # # plot_histogram(traj, geometry, hist_outputpath)
        # plot_space_usage(traj, grid, filename=spus_outputpath, title=reg_string)
        # plot_space_usage(traj, grid, title=reg_string)

    plot_space_usage(space_usage_all / steps_all, grid, filename=spus_outputpath, title=reg_string)
    print("Finished: {}".format(reg_string))


w_exits = np.arange(1, 2.1, 1)
w_walls = np.arange(1, 2.1, 1)
w_doors = np.arange(0, 1.1, 1)
w_directions = np.asarray([False, True])

all = [w_exits, w_walls, w_doors, w_directions]

combinations = list(itertools.product(*all))

pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
pool.map_async(process, combinations[5:6])
pool.close()
pool.join()

#         print('processing: {}'.format(os.path.join(subdir, 'traj.csv')))
#         if os.path.exists(os.path.join(subdir, 'traj.csv')):
#             traj = pd.read_csv(os.path.join(subdir, 'traj.csv'))
#             # traj = traj.loc[traj.step < 200]
#             suffix = subdir.name
#
#             # traj_filename = 'traj/traj_{}.pdf'.format(suffix)
#             # traj_outputpath = os.path.join(output_path, traj_filename)
#             # plot_trajectories(traj, geometry)
#             # # plot_trajectories(traj, geometry, traj_outputpath)
#             #
#             # hist_filename = 'hist/hist_{}.pdf'.format(suffix)
#             # hist_outputpath = os.path.join(output_path, hist_filename)
#             # plot_histogram(traj, geometry)
#             # # plot_histogram(traj, geometry, hist_outputpath)
#
#             spus_filename = 'spus/spus_{}.pdf'.format(suffix)
#             spus_outputpath = os.path.join(output_path, spus_filename)
#             plot_space_usage(traj, geometry, grid)
#             # plot_space_usage(traj, geometry, grid, spus_outputpath)
#         else:
#             print('trajectory does not exist')
#

# traj =  pd.read_csv('data/traj.csv')
# traj = pd.read_csv('results/traj-test/traj.csv')
#
# plot_trajectories(traj, geometry)
# plot_histogram(traj, geometry)
# plot_space_usage(traj, geometry, grid)
