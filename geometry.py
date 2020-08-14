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

    # parameterized constructor
    def __init__(self, filename):
        self.walls = []
        self.floor = None
        self.entrances = {}
        self.exits = {}
        self.pedestrians = {}
        self.edges = []
        self.obstacles = {}
        self.attraction_ground = {}
        self.attraction_mounted = {}
        walls, obstacles, entrances, entrances_properties, exits, edges, attractions_mounted, attractions_ground = read_geometry(
            filename)

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
            p1 = Point(door[0][0], door[0][1])
            p2 = Point(door[1][0], door[1][1])
            self.exits[key] = LineString([p1, p2])

        holes = []
        holes_vis = []
        for key, obstacle in obstacles.items():
            hole_points = []
            hole_points_vis = []
            for point in obstacle:
                hole_points.append((point[0], point[1]))
                hole_points_vis.append(vis.Point(point[0], point[1]))

            hole_points.append(hole_points[0])
            hole_poly = Polygon(hole_points)
            holes.append(hole_points)

            hole_vis = vis.Polygon(hole_points_vis)
            holes_vis.append(hole_vis)

            self.obstacles[key] = hole_poly

        for key, attraction in attractions_ground.items():
            hole_points = []
            hole_points_vis = []

            for point in attraction:
                hole_points.append((point[0], point[1]))
                hole_points_vis.append(vis.Point(point[0], point[1]))

            hole_points.append(hole_points[0])
            hole_poly = Polygon(hole_points)
            holes.append(hole_points)

            hole_vis = vis.Polygon(hole_points_vis)
            holes_vis.append(hole_vis)

            self.attraction_ground[key] = hole_poly

        for key, attraction in attractions_mounted.items():
            hole_points = []
            for point in attraction:
                hole_points.append((point[0], point[1]))
            self.attraction_mounted[key] = Polygon(hole_points)

        # create polygon
        # holes = [(-100000.0, -2000.0), (-100000.0, 2000.0), (-94000.0, 2000.0), (-94000.0, -2000.0), (-100000.0, -2000.0)]
        self.floor = Polygon(points, holes)

        # fig, ax = plt.subplots()
        #
        # patch = PolygonPatch(self.floor, facecolor='blue', edgecolor='black',
        #                      alpha=0.5, zorder=2)
        # ax.add_patch(patch)
        # # plt.plot(*self.floor.interiors.xy)
        # for entrance in self.entrances.values():
        #     x,y = entrance.xy
        #     plt.plot(x,y, color='red')
        # for exit in self.exits.values():
        #     x,y = exit.xy
        #     plt.plot(x,y, color='green')
        #
        # plt.axis('equal')
        # plt.gca().set_adjustable("box")
        #
        # plt.show()
        self.env = vis.Environment([vis.Polygon(points_vis), *holes_vis])
        if not self.env.is_valid(self.epsilon):
            raise ValueError('Check geometry!')
        return

    def is_in_geometry(self, x: float, y: float) -> bool:
        # check if on floor
        # point = sg.Point2(x, y)
        # if self.floor.outer_boundary().oriented_side(point) == sg.Sign.NEGATIVE:
        #     # check if in any of hole
        #     for hole in self.floor.holes:
        #         if hole.oriented_side(point) == sg.Sign.POSITIVE:
        #             return False
        #         for edge in hole.edges:
        #             if sg.squared_distance(edge, point) < THRESHOLD ** 2:
        #                 return False
        #     return True
        # return False
        p = Point(x, y)
        return p.within(self.floor)

    def get_bounding_box(self):
        return self.floor.bounds

    def visible_area(self, x: float, y: float):
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

