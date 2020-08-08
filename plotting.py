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


def plot_geometry(geometry: Geometry):
    plt.figure()
    for key, polygon in geometry.bounds.items():
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black')

    for key, obstacle in geometry.obstacles.items():
        x, y = obstacle.exterior.xy
        plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        plt.plot(x, y, color='gray')

    for key, door in geometry.entrances.items():
        x, y = door.coords.xy
        plt.plot(x, y, color='red')

    plt.show()


def plot_geometry_peds(geometry: Geometry, grid: Grid, peds: Dict[int, Pedestrian], highlight=None):
    draw(geometry.floor, alpha=0.5)

    for key, door in geometry.entrances.items():
        draw(door, color='red', visible_point=False)

    for key, door in geometry.exits.items():
        draw(door, color='blue', visible_point=False)

    for key, ped in peds.items():
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        point = sg.Point2(x, y)

        if ped == highlight:
            draw(point, color='red')
        elif not ped.standing:
            draw(point, color='black')
        else:
            draw(point, color='green')



    plt.show()


def plot_prob_field(geometry: Geometry, grid: Grid, prob_field, title="", ped=None, vmin=None, vmax=None):
    plt.figure()
    plt.title(title)

    # plt.contourf(grid.gridX, grid.gridY, prob_field)
    if not ped == None:
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        # plt.scatter(x, y, color='black')

    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, prob_field, cmap=cm.coolwarm)

    plt.axis('equal')
    plt.xlabel('x/m')
    plt.ylabel('y/m')
    plt.gca().set_adjustable("box")
    plt.colorbar(orientation="horizontal")

    plt.show()


def plot_voronoi_peds(geometry, grid, peds):
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

    plt.show()


def plot_trajectories(geometry: Geometry, grid: Grid, trajectory: Trajectory, peds: Dict[int, Pedestrian]):
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
    draw(geometry.floor, alpha=0.1)

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    plt.show()


def plot_space_usage(geometry: Geometry, grid: Grid, trajectory: Trajectory, num_steps: int):
    plt.figure("Space usage")

    space_usage = trajectory.space_usage[num_steps - 1] / num_steps
    outside = grid.outside_cells
    space_usage = np.ma.MaskedArray(space_usage, outside == 1)

    plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, space_usage, cmap=cm.coolwarm)

    plt.axis('equal')
    plt.gca().set_adjustable("box")
    plt.colorbar()

    plt.show()


def plot_voronoi_neighbors(geometry: Geometry, grid: Grid, voronoi_regions):
    cmap = plt.cm.get_cmap('tab10')

    plt.figure()
    colorValue = 0
    for voronoi_region in voronoi_regions:
        sg.draw.draw(voronoi_region, facecolor=cmap(colorValue))
        colorValue = colorValue + 0.1
    draw(geometry.floor, alpha=0.1)

    plt.show()