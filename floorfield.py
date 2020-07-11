from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg
from skgeom import boolean_set

from distanceCalculator import compute_door_distance, compute_wall_distance, compute_edge_distance, compute_ped_distance
from geometry import Geometry
from grid import Grid, Neighbors
from pedestrian import Pedestrian

from scipy.spatial import Voronoi, voronoi_plot_2d

from plotting import plot_prob_field
from shapely.geometry import Polygon

# for wall distance
wall_b = 2
wall_c = 0.5

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


def distance_to_prob_inc(distance_field, b, c):
    return np.exp(-b * np.exp(-c * (distance_field / 1000)))


def distance_to_prob_dec(distance_field, b, c):
    return 1 - distance_to_prob_inc(distance_field, b, c)


def compute_static_ff(geometry: Geometry, grid: Grid):
    # compute door probability: further is better
    door_distance = compute_door_distance(geometry, grid)
    door_prob = distance_to_prob_inc(door_distance, door_b, door_c)
    # plot_prob_field(geometry, grid, door_prob)

    # compute wall probability: closer is better
    wall_distance = compute_wall_distance(geometry, grid)
    wall_prob = distance_to_prob_dec(wall_distance, wall_b, wall_c)
    # plot_prob_field(geometry, grid, wall_prob)

    # compute distance to edges: closer is better
    exit_distance = compute_edge_distance(geometry, grid)
    exit_prob = distance_to_prob_dec(exit_distance, 10, 1)
    # plot_prob_field(geometry, grid, exit_prob)

    # compute distance to edges: further is better
    # TODO check if maybe as filter
    danger_distance = compute_edge_distance(geometry, grid)
    danger_prob = distance_to_prob_inc(danger_distance, 5, 5)
    # plot_prob_field(geometry, grid, danger_prob)

    # sum everything up for static FF
    static = 1 * door_prob + 5 * wall_prob + 1 * danger_prob + 1 * exit_prob
    static = normalize(static)
    # plot_prob_field(geometry, grid, static)

    return static


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


def compute_prob_neighbors(geometry: Geometry, grid: Grid, ped: Pedestrian, ff):
    prob = {Neighbors.self: 0., Neighbors.left: 0., Neighbors.top: 0., Neighbors.right: 0., Neighbors.bottom: 0.}

    # compute visible area
    x, y = grid.getCoordinates(ped.i(), ped.j())
    visible_area = geometry.visibleArea(x, y)
    vis = Polygon(visible_area.coords)

    # compute voronoi polygons of neighbors
    neighbor_voronoi_polygons = compute_voronoi_neighbors(geometry, grid, ped)

    # sum up every cell in neighbor polygon to neighbor cell
    # sum is weighted by distance, closer = more important
    for key, polygon in neighbor_voronoi_polygons.items():
        p = Polygon(polygon.coords)
        inter = p.intersection(vis)
        points = []
        for ppp in inter.exterior.coords:
            points.append([ppp[0], ppp[1]])
        intersection = sg.Polygon(points)

        weighted_distance = grid.getWeightedDistanceCells(geometry, intersection, sg.Point2(x, y))
        weighted_prob_neighbor = distance_to_prob_dec(weighted_distance, 30, 0.01)
        # plot_prob_field(geometry, grid, weighted_prob_neighbor)
        weighted_prob_neighbor[np.isnan(weighted_prob_neighbor)] = 0
        prob[key] = np.average(weighted_prob_neighbor)
        # TODO prob[Neighbors.self] need to get higher value
    # print(prob)

    # prob_neighbors = np.zeros([3, 3])
    # prob_neighbors[1, 1] = prob[Neighbors.self]
    # prob_neighbors[0, 1] = prob[Neighbors.left]
    # prob_neighbors[1, 0] = prob[Neighbors.top]
    # prob_neighbors[2, 1] = prob[Neighbors.right]
    # prob_neighbors[1, 2] = prob[Neighbors.bottom]

    foo = sum(prob.values())
    for key, p in prob.items():
        prob[key] = p / foo

    return prob


def compute_voronoi_neighbors(geometry: Geometry, grid: Grid, ped: Pedestrian):
    neighbors = grid.getNeighbors(geometry, ped.pos)

    points = {}
    for key, neighbor in neighbors.items():
        if neighbor is not None:
            px, py = grid.getCoordinates(neighbor[0], neighbor[1])
            points[key] = [px, py]

    # dummy points for voronoi computation
    points[1000] = [0, 1000000]
    points[2000] = [0, -1000000]
    points[3000] = [1000000, 0]
    points[4000] = [-1000000, 0]

    points_list = list(points.values())
    vor = Voronoi(list(points.values()))

    polygons = {Neighbors.self: None, Neighbors.left: None, Neighbors.top: None, Neighbors.right: None,
                Neighbors.bottom: None}

    for i in vor.point_region:
        region = vor.regions[i]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            if len(polygon) > 0:
                key = list(points.keys())[
                    list(points.values()).index(points_list[np.where(vor.point_region == i)[0][0]])]
                polygons[key] = sg.Polygon(polygon)

    return polygons
