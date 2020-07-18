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


def plot_geometry_grid(geometry: Geometry, grid: Grid):
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

    for i in range(grid.gridX.shape[0]):
        x = [grid.gridX[i][0], grid.gridX[i][-1]]
        y = [grid.gridY[i], grid.gridY[i]]
        plt.plot(x, y, color='gray', alpha=0.1)

    for i in range(grid.dimX):
        for j in range(grid.dimY):
            x, y = grid.get_coordinates(i, j)
            cellsize = grid.cellsize
            rect = plt.Rectangle((x - 0.5 * cellsize, y - 0.5 * cellsize), cellsize, cellsize, fill=False)
            ax = plt.gca()
            ax.add_patch(rect)

    plt.show()


def plot_geometry_peds(geometry: Geometry, grid: Grid, peds: Dict[int, Pedestrian]):
    # draw(geometry.floor)
    draw(geometry.floor, alpha=0.1)

    for key, door in geometry.entrances.items():
        draw(door, color='red', alpha=0.5)

    for key, door in geometry.exits.items():
        draw(door, color='blue', alpha=0.5)

    for key, ped in peds.items():
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        point = sg.Point2(x, y)
        draw(point, color='black')
    plt.show()


def plot_prob_field(geometry: Geometry, grid: Grid, prob_field):
    plt.figure()

    plt.contourf(grid.gridX, grid.gridY, prob_field)
    plt.colorbar()
    plt.axis('equal')

    # plt.imshow(probField, origin='lower')
    plt.show()


def plot_prob_field_3d(geometry: Geometry, grid: Grid, prob_field):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(grid.gridX, grid.gridY, prob_field, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)

    # plt.contourf(grid.gridX, grid.gridY, prob_field)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    # plt.axis('equal')

    # plt.imshow(probField, origin='lower')
    plt.show()


def plot_voronoi_peds(geometry, grid, peds):
    vdiag = sg.voronoi.VoronoiDiagram()

    for key, ped in peds.items():
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        point = sg.Point2(x, y)
        vdiag.insert(point)
        plt.scatter(x, y)

    # print(vdiag)
    # print(vdiag.sites)
    # for vertix in vdiag.vertices:
    #     print(vertix)
    #     draw(vertix)

    # source, target = he.source(), he.target()
    # if source and target:
    #     plt.plot([source.point().x(), target.point().x()], [source.point().y(), target.point().y()])

    # plt.scatter(npoints[:, 0], npoints[:, 1])

    plt.axis('equal')
    plt.gca().set_adjustable("box")

    draw(geometry.floor, alpha=0.1)

    plt.show()


def plot_trajectories(geometry: Geometry, grid: Grid, trajectory: Trajectory):
    plt.figure()

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
