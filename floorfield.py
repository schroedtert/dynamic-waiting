from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg
from skgeom import boolean_set

from distanceCalculator import compute_door_distance
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian

from scipy.spatial import Voronoi, voronoi_plot_2d

from plotting import plot_prob_field
from shapely.geometry import Polygon

# for wall distance
wall_b = 5
wall_c = 5

# for ped distance
ped_b = 5
ped_c = 1

# for door distance (flow avoidance)
door_b = 10
door_c = 0.5


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)


def normalize(field):
    sum = np.nansum(field)
    return field / sum


def distance_to_prob_inc(distanceField, b, c):
    # b = 10
    # c = 0.5
    # x = np.linspace(-1, 10, 200)
    # y = 1-(np.exp(-b*np.exp(-c*x)))
    # plt.plot(x, y)
    # plt.show()
    # foo =
    # return

    # return np.exp(-np.exp(-0.5*distanceField))
    return np.exp(-b * np.exp(-c * distanceField))


def distance_to_prob_dec(distanceField, b, c):
    return 1 - distance_to_prob_inc(distanceField, b, c)


def compute_static_ff(geometry: Geometry, grid: Grid):
    # doorDistance = compute_door_distance(geometry, grid)
    # # plot_prob_field(geometry, grid, doorDistance)
    # doorProb = distance_to_prob_inc(doorDistance, door_b, door_c)
    # # plot_prob_field(geometry, grid, doorProb)
    # doorProbNormalized = normalize(doorDistance)
    # # plot_prob_field(geometry, grid, doorProbNormalized)
    #
    # # wallDistance = compute_wall_distance(geometry, grid)
    # # plot_prob_field(geometry, grid, wallDistance)
    # # wallProb = distance_to_prob_dec(wallDistance, wall_b, wall_c)
    # # plot_prob_field(geometry, grid, wallProb)
    # # wallProbNormalized = normalize(wallProb)
    # wallProbNormalized = np.zeros_like(grid.gridX)
    #
    # # plot_prob_field(geometry, grid, wallProbNormalized)
    #
    # # dangerDistance = compute_danger_distance(geometry, grid)
    # # plot_prob_field(geometry, grid, dangerDistance)
    #
    # static = doorProbNormalized + wallProbNormalized
    # staticNormalized = normalize(static)
    # # plot_prob_field(geometry, grid, static)
    #
    # # staticFF = np.empty(grid.gridY.shape)
    # # staticFF = np.sqrt(grid.gridX.shape[0] ** 2 + grid.gridX.shape[1])

    doorDistance = compute_door_distance(geometry, grid)
    # plot_prob_field(geometry, grid, doorDistance)

    return 1 - doorDistance


def compute_dynamic_ff(geometry: Geometry, grid: Grid):
    return np.zeros_like(grid.gridX)


def compute_filter_ff(geometry: Geometry, grid: Grid):
    # pedDistance = compute_ped_distance(geometry, grid)
    # plot_prob_field(geometry, grid, pedDistance)
    # pedProb = distance_to_prob_inc(pedDistance, ped_b, ped_c)
    # plot_prob_field(geometry, grid, pedProb)
    # pedProbNormalized = normalize(pedProb)
    # plot_prob_field(geometry, grid, pedProbNormalized)
    return np.ones_like(grid.gridX)


def compute_overall_ff(geometry: Geometry, grid: Grid, staticFF, dynamicFF, filterFF):
    combined = (staticFF + dynamicFF) * filterFF
    # plot_prob_field(geometry, grid, staticFF)
    # plot_prob_field(geometry, grid, dynamicFF)
    # plot_prob_field(geometry, grid, filterFF)
    # plot_prob_field(geometry, grid, combined)

    return combined


def init_dynamic_ff():
    return


# def get_neighbors(geometry: Geometry, grid: Grid, cell: [int, int]):
#     """
#      von Neumann neighborhood
#     """
#     neighbors = []
#     i, j = cell
#
#     possibleNeigbors = []
#     possibleNeigbors.append([i + 1, j])
#     possibleNeigbors.append([i - 1, j])
#     possibleNeigbors.append([i, j + 1])
#     possibleNeigbors.append([i, j - 1])
#
#     if (moore):
#         possibleNeigbors.append([i + 1, j - 1])
#         possibleNeigbors.append([i - 1, j - 1])
#         possibleNeigbors.append([i + 1, j + 1])
#         possibleNeigbors.append([i - 1, j + 1])
#
#     for posNeighbor in possibleNeigbors:
#         x, y = grid.getCoordinates(posNeighbor[0], posNeighbor[1])
#         if geometry.isInGeometry(x, y):
#             neighbors.append(posNeighbor)
#
#     # not shuffling significantly alters the simulation...
#     random.shuffle(neighbors)
#     return neighbors


def computeFFforPed(geometry: Geometry, grid: Grid, ped: Pedestrian, ff):
    x, y = grid.getCoordinates(ped.i(), ped.j())

    neighbors = grid.getNeighbors(geometry, ped.pos)

    points = []
    points.append([x, y])
    for neighbor in neighbors:
        px, py = grid.getCoordinates(neighbor[0], neighbor[1])
        points.append([px, py])

    points.append([0, 1000000])
    points.append([0, -1000000])
    points.append([1000000, 0])
    points.append([-1000000, 0])

    vor = Voronoi(points)

    polygons = []
    for region in vor.regions:
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            if (len(polygon) > 0):
                polygons.append(sg.Polygon(polygon))

    visibleArea = geometry.visibleArea(x, y)
    vis = Polygon(visibleArea.coords)

    for polygon in polygons:
        p = Polygon(polygon.coords)
        inter = p.intersection(vis)
        points = []
        for ppp in inter.exterior.coords:
            points.append([ppp[0], ppp[1]])
        intersection = sg.Polygon(points)
        sg.draw.draw(geometry.floor, alpha=0.2)
        sg.draw.draw(visibleArea, facecolor='blue', alpha=0.2)
        sg.draw.draw(intersection, facecolor='red')
        plt.axis('equal')
        plt.gca().set_adjustable("box")
        plt.show()
    return
