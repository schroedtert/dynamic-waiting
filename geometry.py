from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Tuple

import skgeom as sg
from matplotlib import pyplot as plt

from IO import read_geometry
from pedestrian import Pedestrian
from constants import *

import visilibity as vis

@dataclass
class Geometry:
    """Class for managing the geometry."""
    epsilon = 0.0000001

    walls: List[sg.Segment2]
    edges: List[sg.Segment2]
    floor: sg.PolygonWithHoles
    entrances: Dict[int, sg.Segment2]
    exits: Dict[int, sg.Segment2]
    pedestrians: Dict[int, Pedestrian]
    bounding_box: sg.Bbox2
    obstacles: Dict[int, sg.Polygon]
    attraction_mounted: Dict[int, sg.Polygon]
    attraction_ground: Dict[int, sg.Polygon]

    entrances_properties: Dict[int, Tuple[int, int]]
    arr: sg.arrangement.Arrangement
    env: vis.Environment

    # parameterized constructor
    def __init__(self, filename):
        self.walls = []
        self.floor = None
        self.entrances = {}
        self.exits = {}
        self.pedestrians = {}
        self.edges = []
        self.arr = sg.arrangement.Arrangement()
        self.obstacles = {}
        self.attraction_ground = {}
        self.attraction_mounted = {}
        walls, obstacles, entrances, entrances_properties, exits, edges, attractions_mounted, attractions_ground = read_geometry(
            filename)

        self.entrances_properties = entrances_properties

        points = []
        points_vis = []
        for wall in walls:
            p1 = sg.Point2(wall[0][0], wall[0][1])
            p2 = sg.Point2(wall[1][0], wall[1][1])
            wall = sg.Segment2(p1, p2)
            self.walls.append(wall)
            self.arr.insert(wall)
            points.append(p1)
            points_vis.append(vis.Point(float(p1.x()), float(p1.y())))
        list(OrderedDict.fromkeys(points))

        for edge in edges:
            p1 = sg.Point2(edge[0][0], edge[0][1])
            p2 = sg.Point2(edge[1][0], edge[1][1])
            self.edges.append(sg.Segment2(p1, p2))

        for key, door in entrances.items():
            p1 = sg.Point2(door[0][0], door[0][1])
            p2 = sg.Point2(door[1][0], door[1][1])
            self.entrances[key] = sg.Segment2(p1, p2)

        for key, door in exits.items():
            p1 = sg.Point2(door[0][0], door[0][1])
            p2 = sg.Point2(door[1][0], door[1][1])
            self.exits[key] = sg.Segment2(p1, p2)

        holes = []
        holes_vis = []
        for key, obstacle in obstacles.items():
            hole_points = []
            hole_points_vis = []
            for point in obstacle:
                hole_points.append(sg.Point2(point[0], point[1]))
                hole_points_vis.append(vis.Point(point[0], point[1]))
            hole_poly = sg.Polygon(hole_points)
            holes.append(hole_poly)

            hole_vis = vis.Polygon(hole_points_vis)
            holes_vis.append(hole_vis)

            self.obstacles[key] = hole_poly

            for i in range(len(hole_points)):
                p1 = hole_points[i]
                p2 = hole_points[(i + 1) % len(hole_points)]
                hole_wall = sg.Segment2(p1, p2)
                self.arr.insert(hole_wall)

        for key, attraction in attractions_ground.items():
            hole_points = []
            hole_points_vis = []

            for point in attraction:
                hole_points.append(sg.Point2(point[0], point[1]))
                hole_points_vis.append(vis.Point(point[0], point[1]))

            hole_poly = sg.Polygon(hole_points)
            holes.append(hole_poly)

            hole_vis = vis.Polygon(hole_points_vis)
            # holes_vis.append(hole_vis)

            self.attraction_ground[key] = hole_poly

            for i in range(len(hole_points)):
                p1 = hole_points[i]
                p2 = hole_points[(i + 1) % len(hole_points)]
                hole_wall = sg.Segment2(p1, p2)
                self.arr.insert(hole_wall)

        for key, attraction in attractions_mounted.items():
            hole_points = []
            for point in attraction:
                hole_points.append(sg.Point2(point[0], point[1]))
            self.attraction_mounted[key] = sg.Polygon(hole_points)

        # create polygon
        poly = sg.Polygon(points)
        self.floor = sg.PolygonWithHoles(poly, holes)
        self.bounding_box = poly.bbox()

        self.env = vis.Environment([vis.Polygon(points_vis), *holes_vis])
        print('Environment is valid : ', self.env.is_valid(self.epsilon))
        a = 1

        # for he in self.arr.halfedges:
        #     sg.draw.draw(he.curve())
        # plt.show()
        #
        # vs = sg.RotationalSweepVisibility(self.arr)
        # q = sg.Point2(-60000, 2000)
        # face = self.arr.find(q)
        # vx = vs.compute_visibility(q, face)
        #
        # for he in self.arr.halfedges:
        #     sg.draw.draw(he.curve(), visible_point=False)
        # for v in vx.halfedges:
        #     sg.draw.draw(v.curve(), color='red', visible_point=False)
        #
        # sg.draw.draw(q, color='magenta')
        # plt.show()

        return


    def is_in_geometry(self, x: float, y: float) -> bool:
        # check if on floor
        point = sg.Point2(x, y)
        if self.floor.outer_boundary().oriented_side(point) == sg.Sign.NEGATIVE:
            # check if in any of hole
            for hole in self.floor.holes:
                if hole.oriented_side(point) == sg.Sign.POSITIVE:
                    return False
                for edge in hole.edges:
                    if sg.squared_distance(edge, point) < THRESHOLD ** 2:
                        return False
            return True
        return False

    def get_bounding_box(self):
        return self.bounding_box.xmin(), self.bounding_box.ymin(), self.bounding_box.xmax(), self.bounding_box.ymax()

    def visible_area(self, x: float, y: float):
        # vs = sg.RotationalSweepVisibility(self.arr)
        # q = sg.Point2(x, y)
        #
        # if x == -132000 and y == 2000:
        #     for he in self.arr.halfedges:
        #         sg.draw.draw(he.curve(), visible_point=False)
        #     sg.draw.draw(q, color='magenta')
        #     plt.show()
        # face = self.arr.find(q)
        # vx = vs.compute_visibility(q, face)
        # points = []
        #
        # for v in vx.halfedges:
        #     points.append(v.curve().source())

        # Define the point of the "observer"
        observer = vis.Point(x, y)

        # Necesary to generate the visibility polygon
        observer.snap_to_boundary_of(self.env, self.epsilon)
        observer.snap_to_vertices_of(self.env, self.epsilon)

        # Obtein the visibility polygon of the 'observer' in the environmente
        # previously define
        isovist = vis.Visibility_Polygon(observer, self.env, self.epsilon)
        # point_x, point_y = self.save_print(isovist)

        points = []
        for p in isovist:
            points.append(sg.Point2(p.x(), p.y()))
        # print(point_x)
        # print(point_y)
        # a = 1

        poly = sg.Polygon(points)

        return poly


    @staticmethod
    def save_print(polygon):
        end_pos_x = []
        end_pos_y = []
        for i in range(polygon.n()):
            x = polygon[i].x()
            y = polygon[i].y()

            end_pos_x.append(x)
            end_pos_y.append(y)

        return end_pos_x, end_pos_y

