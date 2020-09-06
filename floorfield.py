from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
from simulation_parameters import SimulationParameters

from distanceCalculator import *
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian
from constants import *
from scipy.spatial import Voronoi, voronoi_plot_2d

from plotting import plot_prob_field
from shapely.geometry import Polygon, Point
from descartes.patch import PolygonPatch


def normalize_dict(field):
    normalization_factor = sum(field.values())
    for key, p in field.items():
        field[key] = p / normalization_factor
    return field


def distance_to_prob_inc(distance_field, b, c):
    return 1 / (1 + np.exp(-c * ((distance_field / 1000) - b)))


def distance_to_prob_dec(distance_field, b, c):
    return 1 - distance_to_prob_inc(distance_field, b, c)


def compute_static_ff(geometry: Geometry, grid: Grid, simulation_parameters: SimulationParameters):
    static = {}

    # compute door probability: further is better
    door_distance = compute_entrance_distance(geometry, grid)
    door_prob = distance_to_prob_inc(door_distance, simulation_parameters.door_b, simulation_parameters.door_c)

    # compute wall probability: closer is better
    wall_distance = compute_wall_distance(geometry, grid)
    wall_prob = distance_to_prob_dec(wall_distance, simulation_parameters.wall_b, simulation_parameters.wall_c)

    for exit_id in geometry.exits.keys():
        # compute distance to exits: closer is better
        exit_distance = compute_exit_distance(geometry, grid, exit_id)
        exit_prob = distance_to_prob_dec(exit_distance, simulation_parameters.exit_b, simulation_parameters.exit_c)

        if simulation_parameters.w_door == 0:
            door_filter = np.ones_like(grid.gridX)
        else:
            door_filter = simulation_parameters.w_door * door_prob

        # sum everything up for static FF
        ff = door_filter \
             * (simulation_parameters.w_wall * wall_prob
                + simulation_parameters.w_exit * exit_prob)

        if simulation_parameters.plot:
            plot_prob_field(geometry, grid, door_filter, "door")
            plot_prob_field(geometry, grid, wall_prob, "wall")
            plot_prob_field(geometry, grid, exit_prob, "exit")
            plot_prob_field(geometry, grid, static, "static")

        static[exit_id] = ff

    return static


def compute_individual_ff(geometry: Geometry, grid: Grid, ped: Pedestrian, simulation_parameters: SimulationParameters):
    if len(geometry.pedestrians.values()) > 1:
        ped_distance = compute_ped_distance(geometry, grid, ped)
        ped_prob = distance_to_prob_inc(ped_distance, simulation_parameters.ped_b, simulation_parameters.ped_c)
    else:
        ped_prob = np.ones_like(grid.gridX)

    return ped_prob


def compute_overall_ff(geometry: Geometry, grid: Grid, static_ff, individual_ff):
    combined = static_ff * individual_ff

    return combined


def init_dynamic_ff():
    return


def compute_prob_neighbors(geometry: Geometry, grid: Grid, ped: Pedestrian, floorfield, weight_direction: bool):
    prob = {}

    # compute visible area
    x, y = grid.get_coordinates(ped.i(), ped.j())
    vis = geometry.visible_area(x, y)

    # compute voronoi polygons of neighbors
    neighbor_voronoi_polygons = compute_voronoi_neighbors(geometry, grid, ped)

    intersections = []

    weight_distance = compute_point_distance(geometry, grid, [ped.i(), ped.j()])
    weight_prob = distance_to_prob_dec(weight_distance, 40, 0.15)

    weighted_floorfield = weight_prob * floorfield

    inside = grid.get_inside_polygon_cells(geometry, vis.exterior.coords)

    # sum up every cell in neighbor polygon to neighbor cell
    # sum is weighted by distance, closer = more important
    for key, polygon in neighbor_voronoi_polygons.items():
        if key == Neighbors.self:
            intersections.append(polygon)
            prob[key] = floorfield.filled(0)[ped.i()][ped.j()]

        elif polygon is not None:
            p = Polygon(polygon.coords)
            inter = p.intersection(vis)

            points = []
            if inter.geom_type == 'Polygon':
                points = inter.exterior.coords
            elif inter.geom_type == 'GeometryCollection':
                for i in inter.geoms:
                    if i.geom_type == 'Polygon':
                        for ppp in i.exterior.coords:
                            points.append([ppp[0], ppp[1]])
            elif inter.geom_type == 'MultiPolygon':
                for i in inter.geoms:
                    if i.geom_type == 'Polygon':
                        for ppp in i.exterior.coords:
                            points.append([ppp[0], ppp[1]])
            else:
                print(inter)

            if len(points) == 0:
                prob[key] = 0
            else:
                intersection = sg.Polygon(points)
                intersections.append(intersection)

                inside_cells = grid.get_inside_polygon_cells(geometry, points)
                combination = inside_cells * weighted_floorfield

                prob[key] = np.ma.max(combination, fill_value=0)


    # weight cells by moving direction
    if weight_direction:
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
