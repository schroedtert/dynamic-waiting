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
from pathlib import Path
from descartes.patch import PolygonPatch
from matplotlib.ticker import FuncFormatter


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


def plot_traj_histogram(traj, geo, filename=None):
    x = traj[traj.step == traj.step.max()].x
    y = traj[traj.step == traj.step.max()].y

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    # the scatter plot:
    ax.scatter(x, y, s=2)
    patch = PolygonPatch(geo.floor, facecolor='gray', edgecolor='black',
                         alpha=0.5, zorder=2)
    ax.add_patch(patch)
    # plt.plot(*self.floor.interiors.xy)
    for entrance in geo.entrances.values():
        ex, ey = entrance.xy
        ax.plot(ex, ey, color='red')
    for exit in geo.exits.values():
        ex, ey = exit.xy
        ax.plot(ex, ey, color='green')

    # for ped_id in traj.id.unique():
    #     df = traj.loc[traj['id'] == ped_id]
    #     df = df.sort_values('step')
    #     ax.plot(df.x, df.y, linewidth=0.3, alpha=0.5)
    ax.set_aspect(1.)

    # create new axes on the right and on the top of the current axes
    # The first argument of the new_vertical(new_horizontal) method is
    # the height (width) of the axes to be created in inches.
    divider = make_axes_locatable(ax)
    axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=ax)
    axHisty = divider.append_axes("right", 1.2, pad=0.1, sharey=ax)

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

    axHistx.set_yticks([0, 2, 4, 6])
    axHisty.set_xticks([0, 10, 20, 30])

    #
    # axHisty.set_xticks([0, 50, 100])
    ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x / 1000), ',')))
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda y, p: format(int(y / 1000), ',')))
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_ylim([-5000, 8000])

    ax.set_xlim([-56000, 8000])
    fig.gca().set_adjustable("box")

    plt.draw()

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='png')
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
    plt.figure(figsize=(10, 2), dpi=300)

    if title is not None:
        plt.title(title)

    # plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage * 100, cmap=cm.jet, vmin=0, vmax=10)

    for entrance in geometry.entrances.values():
        x, y = entrance.xy
        plt.plot(x, y, color='white')
    for exit in geometry.exits.values():
        x, y = exit.xy
        plt.plot(x, y, color='white')

    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage * 100, cmap=cm.jet, vmin=0, vmax=10)

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    # # plt.colorbar(orientation="horizontal")
    cbar = plt.colorbar()
    cbar.set_label('occupation [%]', rotation=90)
    #
    # # plt.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x/1000), ',')))
    # # plt.get_yaxis().set_major_formatter(FuncFormatter(lambda y, p: format(int(y/1000), ',')))
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.ylim([-5, 8])
    plt.xlim([-56, 8])
    # cbar.set_label()
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')
    plt.close()


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

    for subdir in dirs:
        print('Process: {}'.format(os.path.join(subdir, 'traj.csv')))
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

    np.savetxt(os.path.join(output_path, 'spus/{}.txt'.format(reg_string)))
    # plot_space_usage(space_usage_all / steps_all, grid, filename=spus_outputpath, title=reg_string)
    print("Finished: {}".format(reg_string))


def save_space_usage(combination):
    filename = combination[0]
    out_file = combination[1]
    print('Process: {}'.format(filename))
    traj = pd.read_csv(filename)
    space_usage, steps = compute_space_usage(traj, grid)
    space_usage = space_usage / steps
    np.savetxt(out_file, space_usage)


def process_space_usage(combination):
    w_exit = combination[0]
    w_wall = combination[1]
    w_door = combination[2]
    w_direction = combination[3]
    reg_string = 'w-exit={:0.2f}_w-wall={:0.2f}_w-door={:0.2f}_w-directions={:1d}'.format(w_exit, w_wall, w_door,
                                                                                          w_direction)
    regex = re.compile('.+_{}_.+'.format(reg_string))

    space_usage_all = np.zeros_like(grid.gridX)
    number = 0
    for file in os.listdir(directory):
        if number == 10:
            break
        if re.match(regex, file):
            # print(file)
            number = number + 1
            space_usage = np.loadtxt(os.path.join(directory, file))
            space_usage_all = space_usage_all + space_usage
    space_usage_all = space_usage_all / number
    # plot_space_usage(space_usage_all, grid, filename=os.path.join(output_path, reg_string))
    plot_space_usage(space_usage_all, grid, title=reg_string)
    a = 1


def process_trajectories():
    num_repetitions = 1
    max_agents = np.asarray([300])
    init_agents = np.asarray([0.5])
    standing_agents = np.asarray([0.])
    steps = np.asarray([540])
    seeds = np.asarray([1224])
    w_exits = np.asarray([2])
    w_walls = np.asarray([1])
    w_doors = np.asarray([1])
    w_directions = np.asarray([False])

    exit_prob_0 = np.asarray([0.25, 0.5, 0.75])
    all = [max_agents, init_agents, standing_agents,
           steps, seeds, w_exits, w_walls, w_doors, w_directions, exit_prob_0]

    trajs = []

    for combination in itertools.product(*all):
        for rep in range(num_repetitions):
            max_agent = combination[0]
            init_agent = int(max_agent * combination[1])
            standing_agent = int(init_agent * combination[2])
            step = combination[3]
            seed = combination[4]
            w_exit = combination[5]
            w_wall = combination[6]
            w_door = combination[7]
            w_direction = combination[8]
            exit_prob = (combination[9], 1 - combination[9])

            reg_string = "max-agents={:04d}_init-agents={:04d}_standing-agents={:04d}_steps={:04d}_seed={:08d}" \
                         "_w-exit={:0.2f}_w-wall={:0.2f}_w-door={:0.2f}_w-directions={:1d}_exit-prob={:0.2f}-{:0.2f}".format(
                max_agent, init_agent, standing_agent, step, seed, w_exit, w_wall, w_door, int(w_direction),
                exit_prob[0],
                exit_prob[1])

            regex = re.compile('{}'.format(reg_string))

            for subdir in os.scandir(directory):
                if os.path.isdir(subdir) and re.match(regex, subdir.name):
                    if os.path.exists(os.path.join(subdir, 'traj.csv')):
                        print(os.path.join(subdir, 'traj.csv'))
                        trajs.append(pd.read_csv(os.path.join(subdir, 'traj.csv')))
                    else:
                        print('trajectory does not exist')

    i = 0
    for traj in trajs:
        plot_traj_histogram(traj, geometry, filename=os.path.join(output_path, 'hist_{}.png'.format(i)))
        i = i + 1

    a = 1
    # pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    # pool.map_async(process_space_usage, combinations[:])
    # pool.close()
    # pool.join()


file = open('geometries/Bern_geo.xml', 'r')
geometry, grid = init(file)

# directory = r'/run/media/tobias/Ohne Name/2020-femtc/2020-08-17_real-bern-less-people-stair'
# output_path = r'/run/media/tobias/Ohne Name/2020-femtc/2020-08-17_real-bern-plots/traj'
# directory = r'/home/tobias/data/2020-08-17_real-bern-less-people-stair'
# output_path = r'/home/tobias/data/2020-08-17_real-bern-plots/traj'
directory = r'/home/tobias/data/2020-08-17_real-bern-less-people-stair-plots/spus_raw'
output_path = r'/home/tobias/data/2020-08-17_real-bern-less-people-stair-plots/occupation'

if not os.path.exists(output_path):
    os.makedirs(output_path)

# process_trajectories()
w_exits = np.asarray([1, 2])
w_walls = np.asarray([1, 2])
w_doors = np.asarray([1, 0])
w_directions = np.asarray([False])
all = [w_exits, w_walls, w_doors, w_directions]
combinations = list(itertools.product(*all))
for combination in combinations:
    process_space_usage(combination)

# a = 1
#
# # if not os.path.exists(os.path.join(output_path, 'traj')):
# #     os.makedirs(os.path.join(output_path, 'traj'))
# # if not os.path.exists(os.path.join(output_path, 'hist')):
# #     os.makedirs(os.path.join(output_path, 'hist'))
# #
# #
# # traj = pd.read_csv(os.path.join(directory, 'traj.csv'))
# # traj = traj.loc[traj.step < 200]
# # suffix = 'test'
# #
# # traj_filename = 'traj/traj_{}.pdf'.format(suffix)
# # traj_outputpath = os.path.join(output_path, traj_filename)
# # plot_trajectories(traj, geometry, traj_outputpath)
# #
# # hist_filename = 'hist/hist_{}.pdf'.format(suffix)
# # hist_outputpath = os.path.join(output_path, hist_filename)
# # plot_histogram(traj, geometry, hist_outputpath)
# #
# # spus_filename = 'spus/spus_{}.pdf'.format(suffix)
# # spus_outputpath = os.path.join(output_path, spus_filename)
# # plot_space_usage(traj, geometry, grid, spus_outputpath)
#
#
#
#
#
# pool = multiprocessing.Pool(multiprocessing.cpu_count()-2)
# pool.map_async(process, combinations[:])
# pool.close()
# pool.join()
#
# # process(combinations[0])
# #         print('processing: {}'.format(os.path.join(subdir, 'traj.csv')))
# #         if os.path.exists(os.path.join(subdir, 'traj.csv')):
# #             traj = pd.read_csv(os.path.join(subdir, 'traj.csv'))
# #             # traj = traj.loc[traj.step < 200]
# #             suffix = subdir.name
# #
# #             # traj_filename = 'traj/traj_{}.pdf'.format(suffix)
# #             # traj_outputpath = os.path.join(output_path, traj_filename)
# #             # plot_trajectories(traj, geometry)
# #             # # plot_trajectories(traj, geometry, traj_outputpath)
# #             #
# #             # hist_filename = 'hist/hist_{}.pdf'.format(suffix)
# #             # hist_outputpath = os.path.join(output_path, hist_filename)
# #             # plot_histogram(traj, geometry)
# #             # # plot_histogram(traj, geometry, hist_outputpath)
# #
# #             spus_filename = 'spus/spus_{}.pdf'.format(suffix)
# #             spus_outputpath = os.path.join(output_path, spus_filename)
# #             plot_space_usage(traj, geometry, grid)
# #             # plot_space_usage(traj, geometry, grid, spus_outputpath)
# #         else:
# #             print('trajectory does not exist')
# #
#
# # traj =  pd.read_csv('data/traj.csv')
# # traj = pd.read_csv('results/traj-test/traj.csv')
# #
# # plot_trajectories(traj, geometry)
# # plot_histogram(traj, geometry)
# # plot_space_usage(traj, geometry, grid)
