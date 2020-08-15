import random
from dataclasses import dataclass

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from geometry import Geometry
from constants import *
from pedestrian import Pedestrian
from typing import Dict

from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

    inside_cells: np.ndarray
    outside_cells: np.ndarray
    entrance_cells: np.ndarray
    door_cells: Dict[int, np.ndarray]
    exit_cells: Dict[int, np.ndarray]

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

        self.inside_cells = self.__get_inside_cells(geometry)
        self.outside_cells = self.__get_outside_cells(geometry)
        self.door_cells = self.__get_door_cells(geometry)
        self.entrance_cells = self.__get_entrance_cells(geometry)
        self.exit_cells = self.__get_exit_cells(geometry)

    def __get_outside_cells(self, geometry: Geometry):
        outside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                if self.inside_cells[i][j] == 0:
                    outside[i][j] = 1
        return outside

    def __get_inside_cells(self, geometry: Geometry):
        inside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                if geometry.is_in_geometry(x, y):
                    inside[i][j] = 1

        inside = inside + self.__get_entrance_cells(geometry)
        return inside

    def __get_entrance_cells(self, geometry: Geometry):
        entrances = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for key, door in geometry.entrances.items():
                    x, y = self.get_coordinates(i, j)
                    p = Point((x, y))
                    if door.distance(p) < THRESHOLD:
                        entrances[i][j] = 1

        return entrances

    def __get_door_cells(self, geometry: Geometry):
        doors = {}
        for key, door in geometry.entrances.items():
            entrances = np.zeros_like(self.gridX)
            for i in range(self.dimX):
                for j in range(self.dimY):
                    x, y = self.get_coordinates(i, j)
                    p = Point((x, y))
                    if door.distance(p) < THRESHOLD:
                        entrances[i][j] = 1
            doors[key] = entrances

        return doors

    def __get_exit_cells(self, geometry: Geometry):
        exits = {}
        for id, exit in geometry.exits.items():
            exit_cells = np.zeros_like(self.gridX)
            for i in range(self.dimX):
                for j in range(self.dimY):
                    x, y = self.get_coordinates(i, j)
                    p = Point((x, y))
                    if exit.distance(p) < THRESHOLD:
                        exit_cells[i][j] = 1
            exits[id] = exit_cells
        return exits

    def get_ped_cells(self, geometry: Geometry, ped: Pedestrian = None):
        peds = np.zeros_like(self.gridX)

        for key, pped in geometry.pedestrians.items():
            if ped is not None and ped.id != pped.id:
                peds[ped.i()][ped.j()] = 1

        return peds

    def get_wall_cells(self, geometry: Geometry):
        walls = np.zeros_like(self.gridX)

        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = Point((x, y))
                for hole in geometry.obstacles.values():
                    if hole.distance(p) < THRESHOLD:
                        walls[i][j] = 1

        return walls - self.__get_entrance_cells(geometry)

    def get_edge_cells(self, geometry: Geometry):
        edges = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for edge in geometry.edges:
                    x, y = self.get_coordinates(i, j)
                    p = Point((x, y))
                    if edge.distance(p) < THRESHOLD:
                        edges[i][j] = 1

        return edges

    def get_exit_cells(self, geometry: Geometry):
        exits = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for key, door in geometry.exits.items():
                    x, y = self.get_coordinates(i, j)
                    p = Point((x, y))
                    if door.distance(p) < THRESHOLD:
                        exits[i][j] = 1

        return exits

    def get_attraction_ground_cells(self, geometry: Geometry):
        attraction_ground = np.zeros_like(self.gridX)

        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = Point((x, y))
                for hole in geometry.attraction_ground.values():
                    if hole.distance(p) < THRESHOLD:
                        attraction_ground[i][j] = 1

        return attraction_ground

    def get_attraction_mounted_cells(self, geometry: Geometry):
        attraction_mounted = np.zeros_like(self.gridX)

        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.get_coordinates(i, j)
                p = Point((x, y))
                for hole in geometry.attraction_mounted.values():
                    if hole.distance(p) < THRESHOLD:
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

        entrance = self.entrance_cells

        for key, posNeighbor in possibleNeigbors.items():
            if self.inside_cells[posNeighbor[0], posNeighbor[1]] == 1 or entrance[posNeighbor[0]][posNeighbor[1]] == 1:
                neighbors[key] = posNeighbor

        # not shuffling significantly alters the simulation...
        return neighbors

    def get_inside_polygon_cells(self, geometry: Geometry, points):
        inside = np.zeros_like(self.inside_cells)

        verts = []
        for coord in points:
            verts.append((coord[0], coord[1]))

        # print(points)
        # print(verts)
        # print('-----------------------------')
        p = Path(verts, closed=True)

        points = np.vstack((self.gridX.flatten(), self.gridY.flatten())).T

        inside_points = p.contains_points(points)
        mask = inside_points.reshape(self.gridX.shape[0], self.gridX.shape[1])

        mask = np.logical_and(mask, self.inside_cells == 1)
        inside[mask] = 1

        return inside
