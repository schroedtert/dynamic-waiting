from dataclasses import dataclass
import numpy as np
import skgeom as sg

from geometry import Geometry

@dataclass
class Grid:
    '''Class holding the grid information'''
    gridX: np.ndarray
    gridY: np.ndarray
    dimX: int
    dimY: int
    cellsize: float


    def __init__(self, geometry: Geometry, cellsize=0.5):
        minx, miny, maxx, maxy = geometry.getBoundingBox()

        x = np.arange(minx - cellsize, maxx + 2 * cellsize, cellsize)
        y = np.arange(miny - cellsize, maxy + 2 * cellsize, cellsize)

        xv, yv = np.meshgrid(x, y, indexing='ij')
        dimX = len(x)
        dimY = len(y)

        self.gridX = xv
        self.gridY = yv
        self.dimX = dimX
        self.dimY = dimY
        self.cellsize = cellsize

    def getObstacleCells(self, geometry: Geometry):
        obstacleCells = []
        return obstacleCells


    def getOutsideCells(self, geometry: Geometry):
        outside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.getCoordinates(i, j)
                if not geometry.isInGeometry(x,y):
                    outside[i][j] = 1

        return outside


    def getInsideCells(self, geometry: Geometry):
        inside = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                x, y = self.getCoordinates(i, j)
                if geometry.isInGeometry(x,y):
                    inside[i][j] = 1

        return inside

    def getPedCells(self, geometry: Geometry):
        peds = np.zeros_like(self.gridX)

        pedPositions = []
        for key, ped in geometry.peds.items():
            x, y = self.getCoordinates(ped.i(), ped.j())
            pedPositions.append(sg.Point2(x, y))

        for i in range(self.dimX):
            for j in range(self.dimY):
                    x, y = self.getCoordinates(i, j)
                    p = sg.Point2(x,y)

                    for pos in pedPositions:
                        if sg.squared_distance(pos, p) < (0.5 * self.cellsize) ** 2:
                            peds[i][j] = 1

        return peds

    def getWallCells(self, geometry: Geometry):
        walls = np.zeros_like(self.gridX)
        wallSegments = []

        for i in range(len(geometry.floor.outer_boundary().coords)):
            next = (i + 1)%len(geometry.floor.outer_boundary().coords)
            p1 = sg.Point2(geometry.floor.outer_boundary().coords[i][0], geometry.floor.outer_boundary().coords[i][1])
            p2 = sg.Point2(geometry.floor.outer_boundary().coords[next][0], geometry.floor.outer_boundary().coords[next][1])
            wall = sg.Segment2(p1, p2)
            wallSegments.append(wall)

        for hole in geometry.floor.holes:
            for i in range(len(hole.coords)):
                next = (i + 1) % len(hole.coords)
                p1 = sg.Point2(hole.coords[i][0],
                               hole.coords[i][1])
                p2 = sg.Point2(hole.coords[next][0],
                               hole.coords[next][1])
                wall = sg.Segment2(p1, p2)
                wallSegments.append(wall)

        for i in range(self.dimX):
            for j in range(self.dimY):
                for wall in wallSegments:
                    x, y = self.getCoordinates(i, j)
                    p = sg.Point2(x,y)
                    if sg.squared_distance(wall, p) < (0.5*self.cellsize)**2:
                        walls[i][j] = 1
        
        return walls - self.getDoorCells(geometry)

    def getDoorCells(self, geometry: Geometry):
        doors = np.zeros_like(self.gridX)
        for i in range(self.dimX):
            for j in range(self.dimY):
                for key, door in geometry.doors.items():
                    x, y = self.getCoordinates(i, j)
                    p = sg.Point2(x,y)
                    if sg.squared_distance(door, p) < (0.5*self.cellsize)**2:
                        doors[i][j] = 1

        return doors

    def getCoordinates(self, i: int, j: int):
        if 0 <= i < self.dimX and 0 <= j < self.dimY:
            return [self.gridX[i][j], self.gridY[i][j]]

        return [float("inf"), float("inf")]
