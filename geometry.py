from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Final

import skgeom as sg
from matplotlib import pyplot as plt

from IO import read_geometry
from pedestrian import Pedestrian
from constants import *

@dataclass
class Geometry:
    '''Class for managing the geometry.'''
    walls: List[sg.Segment2]
    edges: List[sg.Segment2]
    floor: sg.PolygonWithHoles
    doors: Dict[int, sg.Segment2]
    peds: Dict[int, Pedestrian]
    boundingbox: sg.Bbox2
    arr: sg.arrangement.Arrangement

    # parameterized constructor
    def __init__(self, filename):
        self.walls = []
        self.floor = None
        self.doors = {}
        self.peds = {}
        self.edges = []
        self.arr = sg.arrangement.Arrangement()

        walls, obstacles, doors, edges = read_geometry(filename)

        points = []
        for wall in walls:
            p1 = sg.Point2(wall[0][0], wall[0][1])
            p2 = sg.Point2(wall[1][0], wall[1][1])
            wall = sg.Segment2(p1, p2)
            self.walls.append(wall)
            self.arr.insert(wall)
            points.append(p1)
        list(OrderedDict.fromkeys(points))

        for edge in edges:
            p1 = sg.Point2(edge[0][0], edge[0][1])
            p2 = sg.Point2(edge[1][0], edge[1][1])
            self.edges.append(sg.Segment2(p1, p2))

        for key, door in doors.items():
            p1 = sg.Point2(door[0][0], door[0][1])
            p2 = sg.Point2(door[1][0], door[1][1])
            self.doors[key] = sg.Segment2(p1, p2)

        holes = []
        for key, obstacle in obstacles.items():
            hole_points = []
            for point in obstacle:
                hole_points.append(sg.Point2(point[0], point[1]))
            holes.append(sg.Polygon(hole_points))

            for i in range(len(hole_points)):
                p1 = hole_points[i]
                p2 = hole_points[(i + 1) % len(hole_points)]
                hole_wall = sg.Segment2(p1, p2)
                self.arr.insert(hole_wall)

        # create polygon
        poly = sg.Polygon(points)
        self.floor = sg.PolygonWithHoles(poly, holes)
        self.boundingbox = poly.bbox()

        sg.draw.draw(self.floor)
        plt.show()
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
        return self.boundingbox.xmin(), self.boundingbox.ymin(), self.boundingbox.xmax(), self.boundingbox.ymax()

    def visible_area(self, x: float, y: float):
        vs = sg.RotationalSweepVisibility(self.arr)
        q = sg.Point2(x, y)
        face = self.arr.find(q)
        vx = vs.compute_visibility(q, face)
        points = []

        for v in vx.halfedges:
            points.append(v.curve().source())

        poly = sg.Polygon(points)

        return poly
