from dataclasses import dataclass
from typing import Dict, List

import skgeom as sg

from pedestrian import Pedestrian
from IO import read_geometry

from collections import OrderedDict
import numpy as np
from matplotlib import pyplot as plt
from skgeom.draw import draw

@dataclass
class Geometry:
    '''Class for managing the geometry.'''
    walls: List[sg.Segment2]
    floor: sg.PolygonWithHoles
    doors: Dict[int, sg.Segment2]
    peds: Dict[int, Pedestrian]
    boundingbox: sg.Bbox2

    # parameterized constructor
    def __init__(self, filename):
        self.walls = []
        self.floor = None
        self.doors = {}
        self.peds = {}

        walls, obstacles, doors = read_geometry(filename)

        points = []
        for wall in walls:
            p1 = sg.Point2(wall[0][0], wall[0][1])
            p2 = sg.Point2(wall[1][0], wall[1][1])
            self.walls.append(sg.Segment2(p1, p2))
            points.append(p1)
        list(OrderedDict.fromkeys(points))

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

        # create polygon
        poly = sg.Polygon(points)
        self.floor = sg.PolygonWithHoles(poly, holes)
        self.boundingbox = poly.bbox()

        draw(self.floor)
        plt.show()


    def isInGeometry(self, x: float, y: float) -> bool:
        # check if on floor
        point = sg.Point2(x, y)
        if self.floor.outer_boundary().oriented_side(point) == sg.Sign.NEGATIVE:
            # check if in any of hole
            for hole in self.floor.holes:
                if hole.oriented_side(point) == sg.Sign.POSITIVE:
                    return False
            return True
        return False


    def getBoundingBox(self):
        return self.boundingbox.xmin(), self.boundingbox.ymin(), self.boundingbox.xmax(), self.boundingbox.ymax()