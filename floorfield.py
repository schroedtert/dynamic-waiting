from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg
from skgeom import boolean_set

from distanceCalculator import compute_door_distance, compute_wall_distance, compute_edge_distance, compute_ped_distance
from geometry import Geometry
from grid import Grid
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

def distance_to_prob_inc(distanceField, b, c):
    return np.exp(-b * np.exp(-c * (distanceField / 1000)))


def distance_to_prob_dec(distanceField, b, c):
    return 1 - distance_to_prob_inc(distanceField, b, c)


def compute_static_ff(geometry: Geometry, grid: Grid):
    # compute door probability: further is better
    doorDistance = compute_door_distance(geometry, grid)
    doorProb = distance_to_prob_inc(doorDistance, door_b, door_c)
    plot_prob_field(geometry, grid, doorProb)

    # compute wall probability: closer is better
    wallDistance = compute_wall_distance(geometry, grid)
    wallProb = distance_to_prob_dec(wallDistance, wall_b, wall_c)
    plot_prob_field(geometry, grid, wallProb)

    # compute distance to edges: closer is better
    exitDistance = compute_edge_distance(geometry, grid)
    exitProb = distance_to_prob_dec(exitDistance, 10, 1)
    plot_prob_field(geometry, grid, exitProb)

    # compute distance to edges: further is better
    # TODO check if maybe as filter
    dangerDistance = compute_edge_distance(geometry, grid)
    dangerProb = distance_to_prob_inc(dangerDistance, 5, 5)
    plot_prob_field(geometry, grid, dangerProb)

    # sum everything up for static FF
    static = 1 * doorProb + 5 * wallProb + 1 * dangerProb + 1 * exitProb
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


def computeFFforPed(geometry: Geometry, grid: Grid, ped: Pedestrian, ff):
    x, y = grid.getCoordinates(ped.i(), ped.j())
    origin = sg.Point2(x, y)
    neighbors = grid.getNeighbors(geometry, ped.pos)

    points = []
    for neighbor in neighbors:
        px, py = grid.getCoordinates(neighbor[0], neighbor[1])
        points.append([px, py])

    # dummy points for voronoi computation
    points.append([0, 1000000])
    points.append([0, -1000000])
    points.append([1000000, 0])
    points.append([-1000000, 0])

    vor = Voronoi(points)

    polygons = []
    for i in range(len(vor.regions)):
        region = vor.regions[i]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            if (len(polygon) > 0):
                # print(sg.Polygon(polygon))
                # print(sg.Point2(vor.points[i][0], vor.points[i][1]))
                # polygons[sg.Point2(vor.points[i][0], vor.points[i][1])] = sg.Polygon(polygon)
                # print("")
                polygons.append(sg.Polygon(polygon))

    print(polygons)
    visibleArea = geometry.visibleArea(x, y)
    vis = Polygon(visibleArea.coords)

    doorDistance = compute_door_distance(geometry, grid)
    doorDistance = np.ma.filled(doorDistance, 0)
    plot_prob_field(geometry, grid, doorDistance)

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

        inside = grid.getInsidePolygonCells(intersection)
        # f = inside * doorDistance
        # plot_prob_field(geometry, grid, f)
        insideIntersection = grid.getWeightedDistanceCells(geometry, intersection, sg.Point2(x, y))

        plot_prob_field(geometry, grid, insideIntersection)
        insideIntersection[np.isnan(insideIntersection)] = 0

    return
