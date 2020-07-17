from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg
from skgeom import boolean_set

from distanceCalculator import *
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian
from constants import *
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


def normalize_dict(field):
    normalization_factor = sum(field.values())
    for key, p in field.items():
        field[key] = p / normalization_factor
    return field


def distance_to_prob_inc(distance_field, b, c):
    return np.exp(-b * np.exp(-c * (distance_field / 1000)))


def distance_to_prob_dec(distance_field, b, c):
    return 1 - distance_to_prob_inc(distance_field, b, c)


def compute_static_ff(geometry: Geometry, grid: Grid):
    # compute door probability: further is better
    door_distance = compute_entrance_distance(geometry, grid)
    door_prob = distance_to_prob_inc(door_distance, door_b, door_c)
    plot_prob_field(geometry, grid, door_prob)

    # compute wall probability: closer is better
    wall_distance = compute_wall_distance(geometry, grid)
    wall_prob = distance_to_prob_dec(wall_distance, wall_b, wall_c)
    plot_prob_field(geometry, grid, wall_prob)

    # compute distance to exits: closer is better
    exit_distance = compute_exit_distance(geometry, grid)
    exit_prob = distance_to_prob_dec(exit_distance, 2, 1)

    # compute distance to edges: further is better
    # exit_prob = np.zeros_like(grid.gridX)

    # sum everything up for static FF
    static = 0 * door_prob + 50 * wall_prob + 0 * exit_prob
    static = normalize(static)
    plot_prob_field(geometry, grid, static)

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
    return grid.get_inside_cells(geometry) - grid.get_wall_cells(geometry)


def compute_overall_ff(geometry: Geometry, grid: Grid, staticFF, dynamicFF, filterFF):
    combined = (staticFF + dynamicFF) * filterFF
    # plot_prob_field(geometry, grid, staticFF)
    # plot_prob_field(geometry, grid, dynamicFF)
    # plot_prob_field(geometry, grid, filterFF)
    # plot_prob_field(geometry, grid, combined)

    return combined


def init_dynamic_ff():
    return


def compute_prob_neighbors(geometry: Geometry, grid: Grid, ped: Pedestrian, floorfield):
    # prob = {Neighbors.self: 0., Neighbors.left: 0., Neighbors.top: 0., Neighbors.right: 0., Neighbors.bottom: 0.}
    prob = {}
    # for key, neighbor in grid.get_neighbors(geometry, [ped.i(), ped.j()]).items():
    #     prob[key] = 0.

    size_neighbors = len(grid.get_neighbors(geometry, [ped.i(), ped.j()]).items())

    # compute visible area
    x, y = grid.get_coordinates(ped.i(), ped.j())
    visible_area = geometry.visible_area(x, y)
    vis = Polygon(visible_area.coords)

    # compute voronoi polygons of neighbors
    neighbor_voronoi_polygons = compute_voronoi_neighbors(geometry, grid, ped)

    # sum up every cell in neighbor polygon to neighbor cell
    # sum is weighted by distance, closer = more important
    for key, polygon in neighbor_voronoi_polygons.items():
        if key == Neighbors.self:
            p = 0
            for neighbor in grid.get_neighbors(geometry, [ped.i(), ped.j()]).values():
                p = p + np.ma.filled(floorfield, 0)[neighbor[0]][neighbor[1]]
            prob[key] = p / len(grid.get_neighbors(geometry, [ped.i(), ped.j()]).values())
            print("Neighbor {}: p={}".format(key, p))

            # print(floorfield[ped.i()][ped.j()])
            # prob[key] = np.ma.filled(floorfield, 0)[ped.i()][ped.j()]
        elif polygon is not None:

            points = []

            p = Polygon(polygon.coords)
            inter = p.intersection(vis)

            if inter.geom_type == 'GeometryCollection':
                for i in inter.geoms:
                    if i.geom_type == 'Polygon':
                        for ppp in i.exterior.coords:
                            points.append([ppp[0], ppp[1]])
            else:
                points = []
                for ppp in inter.exterior.coords:
                    points.append([ppp[0], ppp[1]])

            intersection = sg.Polygon(points)

            weighted_distance = grid.get_weighted_distance_cells(geometry, intersection, sg.Point2(x, y))
            weighted_prob_neighbor = distance_to_prob_dec(weighted_distance, 30, 0.01)

            combination = weighted_prob_neighbor * floorfield
            combination[np.isnan(combination)] = 0
            # TODO prob[Neighbors.self] need to get higher value
            # for example: sum of surrounding cells prob
            prob[key] = np.sum(combination)

    # normalize
    # prob = normalize_dict(prob)

    # print("before weighting:")
    # print("{:5f} | {:5f} | {:5f}".format(0., prob[Neighbors.top], 0.))
    # print("{:5f} | {:5f} | {:5f}".format(prob[Neighbors.left], prob[Neighbors.self], prob[Neighbors.right]))
    # print("{:5f} | {:5f} | {:5f}".format(0., prob[Neighbors.bottom], 0.))

    # weight cells by moving direction
    weights = {}
    for key, p in prob.items():
        weights[key] = weighted_neighbors[ped.direction][key]
    weights = normalize_dict(weights)
    for key, p in prob.items():
        prob[key] = p * weights[key]

    # normalize
    prob = normalize_dict(prob)
    # print("after normalization:")
    # print("{:5f} | {:5f} | {:5f}".format(0., prob[Neighbors.top], 0.))
    # print("{:5f} | {:5f} | {:5f}".format(prob[Neighbors.left], prob[Neighbors.self], prob[Neighbors.right]))
    # print("{:5f} | {:5f} | {:5f}".format(0., prob[Neighbors.bottom], 0.))
    return prob


def compute_voronoi_neighbors(geometry: Geometry, grid: Grid, ped: Pedestrian):
    neighbors = grid.get_neighbors(geometry, ped.pos)
    points = {}
    for key, neighbor in neighbors.items():
        if neighbor is not None:
            px, py = grid.get_coordinates(neighbor[0], neighbor[1])
            points[key] = [px, py]

    # dummy points for voronoi computation
    points[1000] = [0, 1000000]
    points[2000] = [0, -1000000]
    points[3000] = [1000000, 0]
    points[4000] = [-1000000, 0]

    points_list = list(points.values())
    vor = Voronoi(list(points.values()))
    polygons = {}
    for key, neighbor in neighbors.items():
        polygons[key] = None

    for i in vor.point_region:
        region = vor.regions[i]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            if len(polygon) > 0:
                key = list(points.keys())[
                    list(points.values()).index(points_list[np.where(vor.point_region == i)[0][0]])]
                polygons[key] = sg.Polygon(polygon)

    return polygons
