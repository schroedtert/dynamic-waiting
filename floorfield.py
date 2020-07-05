from itertools import islice
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg

from distanceCalculator import compute_door_distance
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian

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
    # plot_prob_field(geometry, grid, 1-doorDistance)

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
    print("ped: ({}, {})".format(x, y))
    sg.draw.draw(sg.Point2(x, y))
    neighbors = grid.getNeighbors(geometry, ped.pos)
    vdiag = sg.voronoi.VoronoiDiagram()

    points = []
    vdiag.insert(sg.Point2(x, y))
    for neighbor in neighbors:
        px, py = grid.getCoordinates(neighbor[0], neighbor[1])
        vdiag.insert(sg.Point2(px, py))
        points.append([px, py])

    # vdiag.insert(sg.Point2(1000, 1000))
    # vdiag.insert(sg.Point2(-1000, 1000))
    # vdiag.insert(sg.Point2(1000, -1000))
    # vdiag.insert(sg.Point2(-1000, -1000))
    vdiag.insert(sg.Point2(0, 1000))
    vdiag.insert(sg.Point2(-1000, 0))
    vdiag.insert(sg.Point2(0, -1000))
    vdiag.insert(sg.Point2(1000, -0))

    # points.append(vertex.point())
    # sg.draw.draw(vertex.point())

    # print(np.array([(float(v.x()), float(v.y())) for v in vertex]))
    # sg.draw.draw(sg.Polygon(points))
    # plt.show()

    #     print(vertix)
    #     sg.draw.draw(sg.Polygon(vertix))
    # points = []
    # for he in vdiag.edges:
    #     source, target = he.source(), he.target()
    #     if source and target:
    #         points.append(source.point())
    #         points.append(target.point())
    #
    # sg.draw.draw(sg.Polygon(points))
    # plt.show()

    # print("{} -> {}".format(source.point(), target.point()))
    # plt.plot([source.point().x(), target.point().x()], [source.point().y(), target.point().y()])
    #
    # # plt.scatter(points[:, 0], points[:, 1])
    #
    # plt.axis('equal')
    # plt.gca().set_adjustable("box")
    # plt.gca().set_xlim([-10, 10])
    # plt.gca().set_ylim([-10, 10])

    # print("faces: {}".format(vdiag.number_of_faces()))
    # print([method_name for method_name in dir(vdiag.sites)
    #           if callable(getattr(vdiag.sites, method_name))])
    #
    # for site in vdiag.sites:
    #     print(type(site).__name__)
    #     object_methods = [method_name for method_name in dir(site)
    #                       if callable(getattr(site, method_name))]
    #     print(object_methods)
    #     print("")
    #

    num = 0
    for he in vdiag.edges:
        source, target = he.source(), he.target()
        if source and target:
            num = num + 1
            plt.plot([source.point().x(), target.point().x()], [source.point().y(), target.point().y()])

            plt.axis('equal')
            plt.gca().set_adjustable("box")
            # plt.gca().set_xlim([2.5, 7.5])
            # plt.gca().set_ylim([-5, 0])
            plt.show()

    print(num)

    print(vdiag.__class__)
    l = dir(vdiag)
    pprint(l, indent=2)

    print(nth(vdiag.vertices, 0).__class__)
    l = dir(nth(vdiag.vertices, 0))
    pprint(l, indent=2)

    print(nth(vdiag.edges, 0).__class__)
    l = dir(nth(vdiag.edges, 0))
    pprint(l, indent=2)

    print(nth(vdiag.finite_edges, 0).__class__)
    l = dir(nth(vdiag.finite_edges, 0))
    pprint(l, indent=2)

    print(nth(vdiag.sites, 0).__class__)
    l = dir(nth(vdiag.sites, 0))
    pprint(l, indent=2)

    print("#vertices: {}".format(vdiag.number_of_vertices()))
    print("#edges:    {}".format(vdiag.number_of_halfedges()))
    print("#faces:    {}".format(vdiag.number_of_faces()))
    # print(vdiag.vertices)
    # print([method_name for method_name in dir(vdiag.vertices)
    #           if callable(getattr(vdiag.vertices, method_name))])
    #

    for edge in vdiag.edges:
        print(edge.next())
        print("")

    for i in range(vdiag.number_of_faces()):
        vertex = nth(vdiag.vertices, i)
        edge = nth(vdiag.edges, i)
        edge.curve()
        site = nth(vdiag.sites, i)
        print(site)
        print(vertex.point())
        if (geometry.isInGeometry(site.x(), site.y())):
            sg.draw.draw(site)
            while i < 10:
                source, target = edge.source(), edge.target()
                if source and target:
                    sg.draw.draw(sg.Segment2(source.point(), target.point()))
                edge = edge.next()
                i = i + 1
            plt.axis('equal')
            plt.gca().set_adjustable("box")
            # plt.gca().set_xlim([-10, 10])
            # plt.gca().set_ylim([-10, 10])
            plt.show()
            print("")

    # for edge in vdiag.edges:
    #     print(edge)
    #     i = 0
    #     while i < 5:
    #         source, target = edge.source(), edge.target()
    #         if source and target:
    #             sg.draw.draw(sg.Segment2(source.point(), target.point()))
    #         edge = edge.next()
    #         i = i+1
    #     plt.show()

    # for vertex in vdiag.vertices:
    #     # print(vertex.__class__)
    #     # l = dir(vertex)
    #     # pprint(l, indent=2)
    #     sg.draw.draw(vertex.point())
    # plt.axis('equal')
    # plt.gca().set_adjustable("box")
    # plt.gca().set_xlim([2.5, 7.5])
    # plt.gca().set_ylim([-5, 0])
    #
    # plt.show()

    # source, target = he.source(), he.target()
    # if source and target:
    #     points.append(source.point())
    #     points.append(target.point())

    a = 1
    #     print("vertex: {}".format(vertex.point()))
    #     object_methods = [method_name for method_name in dir(vertex)
    #                       if callable(getattr(vertex, method_name))]
    #     print(object_methods)
    #     print("")
    #
    # print("halfedges: {}".format(vdiag.number_of_halfedges()))
    # print([method_name for method_name in dir(vdiag.edges)
    #           if callable(getattr(vdiag.edges, method_name))])
    # plt.show()
    # for edge in vdiag.edges:
    #     i = 0
    #     pppp = []
    #     while i<10:
    #         source, target = edge.source(), edge.target()
    #         if source and target:
    #             print("{} -> {}".format(source.point(), target.point()))
    #             pppp.append(source.point())
    #             pppp.append(target.point())
    #         edge = edge.next()
    #         i = i +1
    #
    #     sg.draw.draw(sg.Polygon(pppp))
    #     plt.show()
    #     print("")
    #
    #     # object_methods = [method_name for method_name in dir(edge)
    #     #                   if callable(getattr(edge, method_name))]
    #     # print(object_methods)
    #
    #     # print(edge.segment())
    #
    # pp = []
    # for vertex in vdiag.vertices:
    #     pp.append(vertex.point())
    #
    # sg.draw.draw(sg.Polygon(pp[0:5]))
    # plt.axis('equal')
    # plt.gca().set_adjustable("box")
    # plt.gca().set_xlim([-10, 10])
    # plt.gca().set_ylim([-10, 10])
    #
    # plt.show()
    return
