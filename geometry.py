from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
from IO import read_geometry
from pedestrian import Pedestrian
from constants import *

from shapely.geometry import LineString, Point, Polygon
import visilibity as vis
from shapely.ops import cascaded_union

from matplotlib.ticker import FuncFormatter


@dataclass
class Geometry:
    """Class for managing the geometry."""
    epsilon = 0.0000001

    walls: List[LineString]
    edges: List[LineString]
    floor: Polygon
    entrances: Dict[int, LineString]
    exits: Dict[int, LineString]
    pedestrians: Dict[int, Pedestrian]
    obstacles: Dict[int, Polygon]
    attraction_mounted: Dict[int, Polygon]
    attraction_ground: Dict[int, Polygon]

    entrances_properties: Dict[int, Tuple[int, int]]
    env: vis.Environment

    def __init__(self, filename):
        """
        Constructor of geometry, reads the given xml file (filename) and extracts geometrical features
        :param filename: File with geometry information
        """
        self.walls = []
        self.floor = None
        self.entrances = {}
        self.exits = {}
        self.pedestrians = {}
        self.edges = []
        self.obstacles = {}
        self.attraction_ground = {}
        self.attraction_mounted = {}
        walls, obstacles, entrances, entrances_properties, exits, edges = read_geometry(filename)

        self.entrances_properties = entrances_properties

        points = []
        points_vis = []
        for wall in walls:
            p1 = Point(wall[0][0], wall[0][1])
            p2 = Point(wall[1][0], wall[1][1])
            wall = LineString([p1, p2])
            self.walls.append(wall)
            points.append(p1)
            points_vis.append(vis.Point(float(p1.x), float(p1.y)))

        for key, door in entrances.items():
            p1 = Point(door[0][0], door[0][1])
            p2 = Point(door[1][0], door[1][1])
            self.entrances[key] = LineString([p1, p2])
        #
        for key, door in exits.items():
            line_points = []
            for point in door:
                line_points.append(Point(point[0], point[1]))
            self.exits[key] = LineString(line_points)

        holes = []
        holes_vis = []
        for key, obstacle in obstacles.items():
            hole_points = []
            hole_points_vis = []
            for point in obstacle:
                hole_points.append((point[0], point[1]))
                hole_points_vis.append(vis.Point(point[0], point[1]))

            hole_poly = Polygon(hole_points[::-1])
            holes.append(hole_poly)

            hole_vis = vis.Polygon(hole_points_vis)
            holes_vis.append(hole_vis)

            self.obstacles[key] = hole_poly

        # create polygon
        holes_poly = cascaded_union(holes)
        hole_points = []
        holes_vis = []

        if holes_poly.geom_type == 'Polygon':
            coords = holes_poly.exterior.coords[::-1]
            hole_points.append(coords)

            hole_points_vis = []
            for coord in coords[:-1]:
                hole_points_vis.append(vis.Point(coord[0], coord[1]))
            hole_vis = vis.Polygon(hole_points_vis[::-1])
            hole_vis.enforce_standard_form()
            holes_vis.append(hole_vis)

        else:
            for i in holes_poly:
                coords = i.exterior.coords[::-1]
                hole_points.append(coords)

                hole_points_vis = []
                for coord in coords[:-1]:
                    hole_points_vis.append(vis.Point(coord[0], coord[1]))
                hole_vis = vis.Polygon(hole_points_vis[::-1])
                hole_vis.enforce_standard_form()
                holes_vis.append(hole_vis)

        self.floor = Polygon(points, hole_points)

        self.env = vis.Environment([vis.Polygon(points_vis[::-1]), *holes_vis])
        if not self.env.is_valid(self.epsilon):
            raise ValueError('Check geometry!')
        return

    def is_in_geometry(self, x: float, y: float) -> bool:
        """
        Checks whether a given point (x,y) is inside the simulation geometry
        :param x: x coordinate of the point
        :param y: y coordinate of the point
        :return: (x,y) is inside simulation geometry
        """
        p = Point(x, y)
        return p.within(self.floor)

    def get_bounding_box(self):
        """
        :return: Bounding box of the geometry
        """
        return self.floor.bounds

    def visible_area(self, x: float, y: float):
        """
        Computes the visible area from point (x,y)
        :param x: x coordinate of view point
        :param y: y coordinate of view point
        :return: Visibile area from (x,y)
        """
        # Define the point of the "observer"
        observer = vis.Point(x, y)

        # Necessary to generate the visibility polygon
        observer.snap_to_boundary_of(self.env, self.epsilon)
        observer.snap_to_vertices_of(self.env, self.epsilon)

        # Obtain the visibility polygon of the 'observer' in the environment
        # previously defined
        isovist = vis.Visibility_Polygon(observer, self.env, self.epsilon)

        points = []
        for i in range(isovist.n()):
            points.append((isovist[i].x(), isovist[i].y()))

        poly = Polygon(points)

        return poly
