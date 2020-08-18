from pedestrian import Pedestrian
from geometry import Geometry
from grid import Grid
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List
import pandas as pd
import skgeom as sg
from skgeom.draw import draw
from trajectory import Trajectory
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy import ndimage
import numpy as np

from constants import MTOMM
from descartes.patch import PolygonPatch
from matplotlib.ticker import FuncFormatter


def plot_geometry_peds(geometry: Geometry, grid: Grid, peds: Dict[int, Pedestrian], highlight=None, filename=None):
    fig, ax = plt.subplots(dpi=300)

    patch = PolygonPatch(geometry.floor, facecolor='gray', edgecolor='black',
                         alpha=0.5, zorder=2)
    ax.add_patch(patch)
    # plt.plot(*self.floor.interiors.xy)
    for entrance in geometry.entrances.values():
        ex, ey = entrance.xy
        ax.plot(ex, ey, color='red')
    for exit in geometry.exits.values():
        ex, ey = exit.xy
        ax.plot(ex, ey, color='green')
    #
    # for key, ped in peds.items():
    #     x = grid.gridX[ped.i()][ped.j()]
    #     y = grid.gridY[ped.i()][ped.j()]
    #
    #     if ped == highlight:
    #         ax.scatter(x, y, s=5, color='red')
    #     elif not ped.standing:
    #         ax.scatter(x, y, s=5,  color='black')
    #     else:
    #         ax.scatter(x, y, s=5, color='green')

    ax.set_ylim([-5000, 8000])
    ax.set_xlim([-56000, 10000])

    ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x / 1000), ',')))
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda y, p: format(int(y / 1000), ',')))
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_aspect(1.)
    plt.gca().set_adjustable("box")
    # plt.axis('equal')

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='png', bbox_inches='tight')


def plot_prob_field(geometry: Geometry, grid: Grid, prob_field, title="", ped=None, vmin=None, vmax=None,
                    filename=None):
    plt.figure(dpi=300)
    # plt.title(title)

    # plt.contourf(grid.gridX, grid.gridY, prob_field)
    if not ped is None:
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        # plt.scatter(x, y, color='black')

    pc = plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, prob_field, cmap=cm.jet, vmin=0, vmax=2)
    # plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, prob_field, cmap=cm.coolwarm, vmin=0, vmax=2)

    plt.axis('equal')
    plt.xlabel('x/m')
    plt.ylabel('y/m')
    plt.gca().set_adjustable("box")
    # plt.colorbar(orientation="horizontal")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.ylim([-5, 8])
    plt.xlim([-56, 10])

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='png', bbox_inches='tight')


def plot_voronoi_peds(geometry, grid, peds, filename=None):
    vdiag = sg.voronoi.VoronoiDiagram()

    for key, ped in peds.items():
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        point = sg.Point2(x, y)
        vdiag.insert(point)
        plt.scatter(x, y)

    plt.axis('equal')
    plt.gca().set_adjustable("box")

    draw(geometry.floor, alpha=0.1)

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')


def plot_trajectories(geometry: Geometry, grid: Grid, trajectory: Trajectory, peds: Dict[int, Pedestrian],
                      filename=None):
    plt.figure()

    # for key, ped in peds.items():
    #     x = grid.gridX[ped.i()][ped.j()]
    #     y = grid.gridY[ped.i()][ped.j()]
    #     point = sg.Point2(x, y)
    #     draw(point, color='black')

    # plot trajectories
    for ped_id in trajectory.traj.id.unique():
        df = trajectory.traj.loc[trajectory.traj['id'] == ped_id]
        df = df.sort_values('step')
        plt.plot(df.x, df.y)
        # df.plot(x='x', y='y')

    # plot floor
    draw(geometry.floor, alpha=0.1, linewidth=0.01)

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')


def plot_space_usage(geometry: Geometry, grid: Grid, trajectory: Trajectory, num_steps: int, filename=None):
    plt.figure("Space usage")

    space_usage = trajectory.space_usage[num_steps - 1] / num_steps
    outside = grid.outside_cells
    space_usage = np.ma.MaskedArray(space_usage, outside == 1)

    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage, cmap=cm.coolwarm)

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    plt.colorbar()

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')


def plot_voronoi_neighbors(geometry: Geometry, grid: Grid, voronoi_regions, filename=None):
    cmap = plt.cm.get_cmap('tab10')

    plt.figure()
    colorValue = 0
    for voronoi_region in voronoi_regions:
        sg.draw.draw(voronoi_region, facecolor=cmap(colorValue))
        colorValue = colorValue + 0.1
    draw(geometry.floor, alpha=0.1)

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='pdf')
