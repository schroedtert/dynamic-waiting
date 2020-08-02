import random
from dataclasses import dataclass

import numpy as np
import skgeom as sg

from geometry import Geometry
from constants import *
from pedestrian import Pedestrian

moore = False


def cell_is_occupied(geometry: Geometry, cell: [int, int]):
    for ped in geometry.pedestrians.values():
        if cell[0] == ped.i() and cell[1] == ped.j():
            return True

    return False


@dataclass
class Grid:
    """Class holding the grid information"""
    gridX: np.ndarray
    gridY: np.ndarray
    dimX: int
    dimY: int
    cellsize: float

    def __init__(self, geometry: Geometry):
        minx, miny, maxx, maxy = geometry.get_bounding_box()

        x = np.arange(minx - CELLSIZE, maxx + 2 * CELLSIZE, CELLSIZE)
        y = np.arange(miny - CELLSIZE, maxy + 2 * CELLSIZE, CELLSIZE)

        xv, yv = np.meshgrid(x, y, indexing='ij')
        dimX = len(x)
        dimY = len(y)

        self.gridX = xv
        self.gridY = yv
        self.dimX = dimX
        self.dimY = dimY
        self.cellsize = CELLSIZE

    def get_outside_cells(self, geometry: Geometry):
        outside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                if not geometry.is_in_geometry(x, y):
                    outside[i][j] = 1

        return outside

    def get_inside_cells(self, geometry: Geometry):
        inside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                if geometry.is_in_geometry(x, y):
                    inside[i][j] = 1

        inside = inside + self.get_entrance_cells(geometry)
        return inside

    def get_ped_cells(self, geometry: Geometry, ped: Pedestrian = None):
        peds = np.zeros_like(self.gridX)

        pedPositions = []
        for key, pped in geometry.pedestrians.items():
            if ped is not None and ped.id != pped.id:
                x, y = self.get_coordinates(pped.i(), pped.j())
                pedPositions.append(sg.Point2(x, y))

        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = sg.Point2(x, y)

                for pos in pedPositions:
                    if sg.squared_distance(pos, p) < THRESHOLD ** 2:
                        peds[i][j] = 1

        return peds

    def get_wall_cells(self, geometry: Geometry):
        walls = np.zeros_like(self.gridX)
        wallSegments = []

        for hole in geometry.obstacles.values():
            for i in range(len(hole.coords)):
                next_coordinate = (i + 1) % len(hole.coords)
                p1 = sg.Point2(hole.coords[i][0],
                               hole.coords[i][1])
                p2 = sg.Point2(hole.coords[next_coordinate][0],
                               hole.coords[next_coordinate][1])
                wall = sg.Segment2(p1, p2)
                wallSegments.append(wall)

        for i in range(self.dimX):
            for j in range(self.dimY):
                for wall in wallSegments:
                    x, y = self.get_coordinates(i, j)
                    p = sg.Point2(x, y)
                    if sg.squared_distance(wall, p) < THRESHOLD ** 2:
                        walls[i][j] = 1

        return walls - self.get_entrance_cells(geometry)

    def get_edge_cells(self, geometry: Geometry):
        edges = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for edge in geometry.edges:
                    x, y = self.get_coordinates(i, j)
                    p = sg.Point2(x, y)
                    if sg.squared_distance(edge, p) < THRESHOLD ** 2:
                        edges[i][j] = 1

        return edges

    def get_danger_cells(self, geometry: Geometry):
        edges = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for edge in geometry.edges:
                    x, y = self.get_coordinates(i, j)
                    p = sg.Point2(x, y)
                    if sg.squared_distance(edge, p) < 1:
                        edges[i][j] = 1

        return edges

    def get_entrance_cells(self, geometry: Geometry):
        entrances = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for key, door in geometry.entrances.items():
                    x, y = self.get_coordinates(i, j)
                    p = sg.Point2(x, y)
                    if sg.squared_distance(door, p) < THRESHOLD ** 2:
                        entrances[i][j] = 1

        return entrances

    def get_exit_cells(self, geometry: Geometry):
        exits = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for key, door in geometry.exits.items():
                    x, y = self.get_coordinates(i, j)
                    p = sg.Point2(x, y)
                    if sg.squared_distance(door, p) < THRESHOLD ** 2:
                        exits[i][j] = 1

        return exits

    def get_attraction_ground_cells(self, geometry: Geometry):
        attraction_ground = np.zeros_like(self.gridX)

        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = sg.Point2(x, y)
                for hole in geometry.attraction_ground.values():
                    if hole.oriented_side(p) != sg.Sign.NEGATIVE:
                        attraction_ground[i][j] = 1

        return attraction_ground

    def get_attraction_mounted_cells(self, geometry: Geometry):
        attraction_mounted = np.zeros_like(self.gridX)

        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = sg.Point2(x, y)
                for hole in geometry.attraction_mounted.values():
                    if hole.oriented_side(p) != sg.Sign.NEGATIVE:
                        attraction_mounted[i][j] = 1

        return attraction_mounted

    def get_coordinates(self, i: int, j: int):
        if 0 <= i < self.dimX and 0 <= j < self.dimY:
            return [self.gridX[i][j], self.gridY[i][j]]

        return [float("inf"), float("inf")]

    def get_neighbors(self, geometry: Geometry, cell: [int, int]):
        """
         von Neumann neighborhood
        """
        neighbors = {}
        i, j = cell

        possibleNeigbors = {}
        possibleNeigbors[Neighbors.self] = [i, j]
        possibleNeigbors[Neighbors.left] = [i - 1, j]
        possibleNeigbors[Neighbors.top] = [i, j + 1]
        possibleNeigbors[Neighbors.right] = [i + 1, j]
        possibleNeigbors[Neighbors.bottom] = [i, j - 1]

        entrance = self.get_entrance_cells(geometry)

        for key, posNeighbor in possibleNeigbors.items():
            x, y = self.get_coordinates(posNeighbor[0], posNeighbor[1])
            if geometry.is_in_geometry(x, y) or entrance[posNeighbor[0]][posNeighbor[1]] == 1:
                neighbors[key] = posNeighbor

        # not shuffling significantly alters the simulation...
        return neighbors

    def get_inside_polygon_cells(self, polygon: sg.Polygon):
        inside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                if polygon.oriented_side(sg.Point2(x, y)) == sg.Sign.NEGATIVE:
                    inside[i][j] = 1

        return inside

    def get_weighted_distance_cells(self, geometry: Geometry, polygon: sg.Polygon, point: sg.Point2):
        inside = self.get_inside_cells(geometry)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = sg.Point2(x, y)
                if polygon.oriented_side(p) == sg.Sign.NEGATIVE:
                    inside[i][j] = np.sqrt(sg.squared_distance(p, point))
                else:
                    inside[i][j] = np.nan
        return inside

    def get_nearby_cells(self, geometry: Geometry, cell: [int, int], cutoff: float):
        px, py = self.get_coordinates(cell[0], cell[1])
        reference = sg.Point2(px, py)

        nearby = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = sg.Point2(x, y)
                if sg.squared_distance(reference, p) < cutoff ** 2:
                    nearby[i][j] = 1

        return nearby

