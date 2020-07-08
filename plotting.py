from pedestrian import Pedestrian
from geometry import Geometry
from grid import Grid
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List
import pandas as pd
import skgeom as sg
from skgeom.draw import draw


def plot_geometry(geometry: Geometry):
    plt.figure()
    for key, polygon in geometry.bounds.items():
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black')

    for key, obstacle in geometry.obstacles.items():
        x, y = obstacle.exterior.xy
        plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        plt.plot(x, y, color='gray')

    for key, door in geometry.doors.items():
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

    for key, door in geometry.doors.items():
        x, y = door.coords.xy
        plt.plot(x, y, color='red')

    for i in range(grid.gridX.shape[0]):
        x = [grid.gridX[i][0], grid.gridX[i][-1]]
        y = [grid.gridY[i], grid.gridY[i]]
        plt.plot(x, y, color='gray', alpha=0.1)

    for i in range(grid.dimX):
        for j in range(grid.dimY):
            x, y = grid.getCoordinates(i, j)
            cellsize = grid.cellsize
            rect = plt.Rectangle((x - 0.5 * cellsize, y - 0.5 * cellsize), cellsize, cellsize, fill=False)
            ax = plt.gca()
            ax.add_patch(rect)

    plt.show()


def plot_geometry_peds(geometry: Geometry, grid: Grid, peds: Dict[int, Pedestrian]):
    # draw(geometry.floor)
    draw(geometry.floor, alpha=0.1)

    for key, door in geometry.doors.items():
        draw(door, color='red', alpha=0.5)

    for key, ped in peds.items():
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]
        point = sg.Point2(x, y)
        draw(point, color='black')
        # plt.figure()
        # for key, polygon in geometry.bounds.items():
        #     x, y = polygon.exterior.xy
        #     plt.plot(x, y, color='black')
        #
        # for key, obstacle in geometry.obstacles.items():
        #     x, y = obstacle.exterior.xy
        #     plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        #     plt.plot(x, y, color='gray')
        #
        # for key, door in geometry.doors.items():
        #     x, y = door.coords.xy
        #     plt.plot(x, y, color='red')
        #
        # for key, ped in peds.items():
        #     x = grid.gridX[ped.i()][ped.j()]
        #     y = grid.gridY[ped.i()][ped.j()]
        #
        #     plt.plot(x, y, color='blue', markersize='8', marker='o')
    plt.show()


def plot_marked_zells(geometry: Geometry, grid: Grid, marked_cells: [[int, int]]):
    print(marked_cells)
    plt.figure()
    # for key, polygon in geometry.bounds.items():
    #     x, y = polygon.exterior.xy
    #     plt.plot(x, y, color='black')
    #
    # for key, obstacle in geometry.obstacles.items():
    #     x, y = obstacle.exterior.xy
    #     plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
    #     plt.plot(x, y, color='gray')

    # for key, door in geometry.doors.items():
    #     x, y = door.coords.xy
    #     plt.plot(x, y, color='red')
    for cell in marked_cells:
        x, y = grid.getCoordinates(cell[0], cell[1])
        cellsize = grid.cellsize
        rect = plt.Rectangle((x - 0.5 * cellsize, y - 0.5 * cellsize), cellsize, cellsize, fill=True)
        ax = plt.gca()
        ax.add_patch(rect)

    plt.show()


def plot_prob_field(geometry: Geometry, grid: Grid, probField):
    plt.figure()
    # plt.contour(grid.gridX, grid.gridY, phi, [0], linewidths=(3), colors='black')
    # for key, door in geometry.doors.items():
    #     draw(door, color='red', alpha=0.5)

    plt.contourf(grid.gridX, grid.gridY, probField)
    plt.colorbar()
    plt.axis('equal')

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
    # plt.gca().set_xlim([-10.5, 10.5])
    # plt.gca().set_ylim([-10, 10])

    draw(geometry.floor, alpha=0.1)

    plt.show()
