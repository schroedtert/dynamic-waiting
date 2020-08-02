from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg
from skgeom import boolean_set
from simulation_parameters import SimulationParameters
from distanceCalculator import *
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian
from constants import *
from scipy.spatial import Voronoi, voronoi_plot_2d

from plotting import plot_prob_field
from shapely.geometry import Polygon


def nth(iterable, n, default=None):
    """Returns the nth item or a default value"""
    return next(islice(iterable, n, None), default)


def normalize_dict(field):
    normalization_factor = sum(field.values())
    for key, p in field.items():
        field[key] = p / normalization_factor
    return field


def distance_to_prob_inc(distance_field, b, c):
    return np.exp(-b * np.exp(-c * (distance_field / 1000)))


def distance_to_prob_dec(distance_field, b, c):
    return 1 - distance_to_prob_inc(distance_field, b, c)


def compute_static_ff(geometry: Geometry, grid: Grid, simulation_parameters: SimulationParameters):
    # compute door probability: further is better
    door_distance = compute_entrance_distance(geometry, grid)
    # plot_prob_field(geometry, grid, door_distance, "entrance distance")
    door_prob = distance_to_prob_inc(door_distance, simulation_parameters.door_b, simulation_parameters.door_c)
    # plot_prob_field(geometry, grid, door_prob, "entrance prob")

    # compute wall probability: closer is better
    wall_distance = compute_wall_distance(geometry, grid)
    # plot_prob_field(geometry, grid, wall_distance, "wall distance")
    wall_prob = distance_to_prob_dec(wall_distance, simulation_parameters.wall_b, simulation_parameters.wall_c)
    # plot_prob_field(geometry, grid, wall_prob, "wall prob")

    # compute distance to exits: closer is better
    exit_distance = compute_exit_distance(geometry, grid)
    # plot_prob_field(geometry, grid, exit_distance, "exit distance")
    exit_prob = distance_to_prob_dec(exit_distance, simulation_parameters.exit_b, simulation_parameters.exit_c)
    # plot_prob_field(geometry, grid, exit_prob, "exit prob")

    # compute distance to ground attraction points: closer is better
    attraction_ground_distance = compute_attraction_ground_distance(geometry, grid)
    # plot_prob_field(geometry, grid, attraction_ground_distance, "attraction ground distance")
    attraction_ground_prob = distance_to_prob_dec(attraction_ground_distance, simulation_parameters.attraction_ground_b,
                                                  simulation_parameters.attraction_ground_c)
    # plot_prob_field(geometry, grid, attraction_ground_prob, "attraction ground prob")

    # compute distance to ground attraction points: closer is better
    attraction_mounted_distance = compute_attraction_mounted_distance(geometry, grid)
    # plot_prob_field(geometry, grid, attraction_mounted_distance, "attraction mounted distance")
    attraction_mounted_prob = distance_to_prob_dec(attraction_mounted_distance,
                                                   simulation_parameters.attraction_mounted_b,
                                                   simulation_parameters.attraction_mounted_c)
    # plot_prob_field(geometry, grid, attraction_mounted_prob, "attraction_mounted_prob")

    # sum everything up for static FF
    static = simulation_parameters.w_door * door_prob \
             + simulation_parameters.w_wall * wall_prob \
             + simulation_parameters.w_exit * exit_prob \
             + simulation_parameters.w_attraction_ground * attraction_ground_prob \
             + simulation_parameters.w_attraction_mounted * attraction_mounted_prob

    plot_prob_field(geometry, grid, static, "static")

    return static


def compute_individual_ff(geometry: Geometry, grid: Grid, ped: Pedestrian, simulation_parameters: SimulationParameters):
    if len(geometry.pedestrians.values()) > 1:
        ped_distance = compute_ped_distance(geometry, grid, ped)
        # plot_prob_field(geometry, grid, ped_distance, "ped distance")
        ped_prob = distance_to_prob_inc(ped_distance, simulation_parameters.ped_b, simulation_parameters.ped_c)
    else:
        ped_prob = np.ones_like(grid.gridX)

    # plot_prob_field(geometry, grid, ped_prob, "ped prob")
    return ped_prob


def compute_overall_ff(geometry: Geometry, grid: Grid, static_ff, individual_ff):
    combined = static_ff * individual_ff
    # plot_prob_field(geometry, grid, static_ff)
    # plot_prob_field(geometry, grid, individual_ff)
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

    weight_distance = compute_point_distance(geometry, grid, [ped.i(), ped.j()])
    weight_prob = distance_to_prob_dec(weight_distance, 5, 0.25)

    weighted_floorfield = weight_prob * floorfield

    # sum up every cell in neighbor polygon to neighbor cell
    # sum is weighted by distance, closer = more important
    for key, polygon in neighbor_voronoi_polygons.items():
        if key == Neighbors.self:
            # all cells within a 2m? range
            # distance = 500
            # nearby = grid.get_nearby_cells(geometry, [ped.i(), ped.j()], distance)

            # a = grid.get_weighted_distance_cells(geometry, floorfield, sg.Point2(x, y))
            # plot_prob_field(geometry, grid, nearby*grid.get_inside_cells(geometry))
            # foo = nearby * floorfield
            # plot_prob_field(geometry, grid, foo)
            # prob[key] = np.max(foo)
            prob[key] = floorfield.filled(0)[ped.i()][ped.j()]

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

            inside_cells = grid.get_inside_polygon_cells(geometry, intersection, sg.Point2(x, y))
            combination = inside_cells * weighted_floorfield
            prob[key] = np.ma.max(combination, fill_value=0)

    # for intersection in intersections:
    #     sg.draw.draw(intersection)
    # sg.draw.draw(geometry.floor, alpha=0.2)
    # plt.show()

    # weight cells by moving direction
    weights = {}
    for key, p in prob.items():
        weights[key] = weighted_neighbors[ped.direction][key]
    weights = normalize_dict(weights)
    for key, p in prob.items():
        prob[key] = p * weights[key]

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
        if -1 not in region:
            polygon = [vor.vertices[i] for i in region]
            if len(polygon) > 0:
                key = list(points.keys())[
                    list(points.values()).index(points_list[np.where(vor.point_region == i)[0][0]])]
                polygons[key] = sg.Polygon(polygon)

    return polygons
