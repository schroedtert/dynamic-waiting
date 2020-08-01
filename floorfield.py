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
wall_b = 1
wall_c = 1

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
    # plot_prob_field(geometry, grid, door_prob, "entrance prob")

    # compute wall probability: closer is better
    wall_distance = compute_wall_distance(geometry, grid)
    wall_prob = distance_to_prob_dec(wall_distance, wall_b, wall_c)
    # plot_prob_field(geometry, grid, wall_prob, "wall prob")

    # compute distance to exits: closer is better
    exit_distance = compute_exit_distance(geometry, grid)
    exit_prob = distance_to_prob_dec(exit_distance, 5, 0.5)
    # plot_prob_field(geometry, grid, exit_prob, "exit prob")

    # compute distance to ground attraction points: closer is better
    attraction_ground_distance = compute_attraction_ground_distance(geometry, grid)
    attraction_ground_prob = distance_to_prob_dec(attraction_ground_distance, 2, 0.5)
    # plot_prob_field(geometry, grid, attraction_ground_prob, "attraction ground prob")

    # compute distance to ground attraction points: closer is better
    attraction_mounted_distance = compute_attraction_mounted_distance(geometry, grid)
    attraction_mounted_prob = distance_to_prob_dec(attraction_mounted_distance, 2, 0.1)
    # plot_prob_field(geometry, grid, attraction_mounted_prob, "attraction_mounted_prob")

    # sum everything up for static FF
    static = 0.5 * door_prob + 1 * wall_prob + 1 * exit_prob + 1 * attraction_ground_prob + 1 * attraction_mounted_prob
    plot_prob_field(geometry, grid, static, "static")

    return static


def compute_dynamic_ff(geometry: Geometry, grid: Grid, ped: Pedestrian):
    return np.zeros_like(grid.gridX)


def compute_filter_ff(geometry: Geometry, grid: Grid, ped: Pedestrian):
    pedDistance = compute_ped_distance(geometry, grid, ped)
    plot_prob_field(geometry, grid, pedDistance, "ped distance")
    # plot_geometry_peds(geometry, grid, {0: geometry.peds[0]})
    pedProb = distance_to_prob_inc(pedDistance, ped_b, ped_c)
    plot_prob_field(geometry, grid, pedProb, "ped prob")
    # pedProbNormalized = normalize(pedProb)
    # plot_prob_field(geometry, grid, pedProbNormalized)
    return pedProb


def compute_overall_ff(geometry: Geometry, grid: Grid, staticFF, dynamicFF, filterFF):
    combined = (staticFF + dynamicFF) * filterFF
    # plot_prob_field(geometry, grid, staticFF)
    # plot_prob_field(geometry, grid, dynamicFF)
    # plot_prob_field(geometry, grid, filterFF)
    # plot_prob_field(geometry, grid, combined, "overall")

    return combined


def init_dynamic_ff():
    return


def compute_prob_neighbors(geometry: Geometry, grid: Grid, ped: Pedestrian, floorfield):
    prob = {}

    # compute visible area
    x, y = grid.get_coordinates(ped.i(), ped.j())
    visible_area = geometry.visible_area(x, y)
    vis = Polygon(visible_area.coords)

    # compute voronoi polygons of neighbors
    neighbor_voronoi_polygons = compute_voronoi_neighbors(geometry, grid, ped)

    intersections = []
    weights = np.zeros_like(grid.gridX)
    # sum up every cell in neighbor polygon to neighbor cell
    # sum is weighted by distance, closer = more important
    for key, polygon in neighbor_voronoi_polygons.items():
        if key == Neighbors.self:
            # all cells within a 2m? range
            distance = 500
            nearby = grid.get_nearby_cells(geometry, [ped.i(), ped.j()], distance)

            # a = grid.get_weighted_distance_cells(geometry, floorfield, sg.Point2(x, y))
            # plot_prob_field(geometry, grid, nearby*grid.get_inside_cells(geometry))
            foo = nearby * floorfield
            # plot_prob_field(geometry, grid, foo)
            prob[key] = np.max(foo)
            # asd = 1

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
            intersections.append(intersection)
            weighted_distance = grid.get_weighted_distance_cells(geometry, intersection, sg.Point2(x, y))
            # plot_prob_field(geometry, grid, weighted_distance, 'weight distance')
            weighted_prob_neighbor = distance_to_prob_dec(weighted_distance, 5, 0.25)

            weighted_prob_neighbor[np.isnan(weighted_prob_neighbor)] = 0
            # plot_prob_field(geometry, grid, weighted_prob_neighbor, 'weight distance')

            combination = weighted_prob_neighbor * floorfield
            combination[np.isnan(combination)] = 0
            plot_prob_field(geometry, grid, combination, 'weighted neighborhood')

            prob[key] = np.max(combination)
            weights = weights + combination

    # plot_prob_field(geometry, grid, weights, 'weight distance')
    #
    #
    # for intersection in intersections:
    #     sg.draw.draw(intersection)
    # sg.draw.draw(geometry.floor, alpha=0.2)
    # plt.show()

    # weight cells by moving direction
    # weights = {}
    # for key, p in prob.items():
    #     weights[key] = weighted_neighbors[ped.direction][key]
    # weights = normalize_dict(weights)
    # for key, p in prob.items():
    #     prob[key] = p * weights[key]

    prob = normalize_dict(prob)
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
