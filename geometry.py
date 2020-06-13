from dataclasses import dataclass
from shapely.geometry import Polygon, LineString, Point
from typing import Dict, List

from pedestrian import Pedestrian

import numpy as np

@dataclass
class Geometry:
    '''Class for managing the geometry.'''
    bounds: Dict[int, Polygon]
    obstacles: Dict[int, Polygon]
    doors: Dict[int, LineString]
    peds: Dict[int, Pedestrian]

    def isInGeometry(self, x: float, y:float) -> bool:
        isInRoom = False

        p = Point(x, y)
        for key, room in self.bounds.items():
            if room.contains(p):
                isInRoom = True
                break

        if isInRoom:
            for key, obstacle in self.obstacles.items():
                if obstacle.contains(p):
                    return False
            return True

        return False

@dataclass
class Grid:
    '''Class holding the grid information'''
    gridX: np.ndarray
    gridY: np.ndarray
    dimX: int
    dimY: int
    cellsize: float

    def getOutsideCells(self, geometry: Geometry):
        outsideCells = []
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.getCoordinates(i, j)
                if not geometry.isInGeometry(x,y):
                    outsideCells.append([i, j])

        return outsideCells


    def getInsideCells(self, geometry: Geometry):
        insideCells = []
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.getCoordinates(i, j)
                if geometry.isInGeometry(x,y):
                    insideCells.append([i, j])

        return insideCells


    def getWallCells(self, geometry: Geometry):
        wallCells = []
        # for i in range(self.dimX):
        #     for j in range(self.dimY):
                # for key, door in geometry.doors.items():
                #     x, y = self.getCoordinates(i, j)
                #     p = Point(x,y)
                #     if door.distance(p) < 1e-5:
                #         wallCells.append([i, j])

        return wallCells

    def getDoorCells(self, geometry: Geometry):
        doorCells = []
        for i in range(self.dimX):
            for j in range(self.dimY):
                for key, door in geometry.doors.items():
                    x, y = self.getCoordinates(i, j)
                    p = Point(x,y)
                    if door.distance(p) < 1e-5:
                        doorCells.append([i, j])

        print(doorCells)
        return doorCells

    def getCoordinates(self, i: int, j: int):
        if 0 <= i < self.dimX and 0 <= j < self.dimY:
            return [self.gridX[i][j], self.gridY[i][j]]

        return [float("inf"), float("inf")]

    def create(geometry: Geometry, cellsize=0.5):
        minx = float("inf")
        miny = float("inf")
        maxx = -float("inf")
        maxy = -float("inf")

        for key, room in geometry.bounds.items():
            tmpminx, tmpminy, tmpmaxx, tmpmaxy = room.bounds
            minx = min(minx, tmpminx)
            miny = min(miny, tmpminy)
            maxx = max(maxx, tmpmaxx)
            maxy = max(maxy, tmpmaxy)

        x = np.arange(minx - cellsize, maxx + 2 * cellsize, cellsize)
        y = np.arange(miny - cellsize, maxy + 2 * cellsize, cellsize)

        xv, yv = np.meshgrid(x, y, indexing='ij')
        dimX = len(x)
        dimY = len(y)
        return Grid(xv, yv, dimX, dimY, cellsize)
