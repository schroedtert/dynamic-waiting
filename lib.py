import itertools as it # for cartesian product
import time
import random
import os
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl

from IO import *
from geometry import  *
import skfmm

logfile = 'log.dat'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
moore = False

def init(file, cellSize):
    geometry = read_geometry(file)
    grid = Grid.create(geometry, cellSize)
    # grid = create_grid(geometry, cellSize)
    return geometry, grid


def create_peds(numPeds: int, geometry: Geometry, grid:Grid):
    minx = float("inf")
    miny = float("inf")
    maxx = -float("inf")
    maxy = -float("inf")

    for key, polygon in geometry.bounds.items():
        tmpminx, tmpminy, tmpmaxx, tmpmaxy = polygon.bounds
        minx = min(minx, tmpminx)
        miny = min(miny, tmpminy)
        maxx = max(maxx, tmpmaxx)
        maxy = max(maxy, tmpmaxy)

    for index in range(numPeds):
        while True:
            i = random.randint(0, grid.gridX.shape[0]-1)
            j = random.randint(0, grid.gridY.shape[1]-1)
            occupied = False
            for id, ped in geometry.peds.items():
                if ped.i() == i and ped.j() == j:
                   occupied = True
                   break

            x, y = grid.getCoordinates(i, j)
            if not occupied and geometry.isInGeometry(x, y):
                geometry.peds[index] = Pedestrian([i, j])
                # print("{:02d} {:5.2f} {:5.2f}".format(index, x, y))
                break

def compute_door_distance(geometry: Geometry, grid: Grid):
    phi = -1 * np.ones_like(grid.gridX)
    doorCells = grid.getDoorCells(geometry)

    for doorCell in doorCells:
        phi[doorCell[0]][doorCell[1]] = 1

    phi[grid.gridX > 10] = 1

    outsideCells = grid.getOutsideCells(geometry)

    outsideMask = np.full(grid.gridX.shape, True)
    for outside in outsideCells:
        outsideMask[outside[0]][outside[1]] = False

    phi = np.ma.MaskedArray(phi, outsideMask)
    d = skfmm.distance(phi, dx=grid.cellsize)
    return d


def compute_wall_distance(geometry: Geometry, grid: Grid):

    return


def compute_static_ff(geometry: Geometry, grid: Grid):
    staticFF = np.empty(grid.gridY.shape)
    staticFF = np.sqrt(grid.gridX.shape[0]**2 + grid.gridX.shape[1])

    return staticFF

def init_dynamic_ff():
    return

def compute_dynamic_ff():
    return

def get_neighbors(geometry: Geometry, grid: Grid, cell:[int, int]):
    """
     von Neumann neighborhood
    """
    neighbors = []
    i, j = cell

    possibleNeigbors = []
    possibleNeigbors.append([i + 1, j])
    possibleNeigbors.append([i - 1, j])
    possibleNeigbors.append([i, j + 1])
    possibleNeigbors.append([i, j - 1])

    if (moore):
        possibleNeigbors.append([i + 1, j - 1])
        possibleNeigbors.append([i - 1, j - 1])
        possibleNeigbors.append([i + 1, j + 1])
        possibleNeigbors.append([i - 1, j + 1])

    for posNeighbor in possibleNeigbors:
        x,y = grid.getCoordinates(posNeighbor[0], posNeighbor[1])
        if geometry.isInGeometry(x, y):
            neighbors.append(posNeighbor)

    # not shuffling significantly alters the simulation...
    random.shuffle(neighbors)
    return neighbors

def run_simulation(file, numPeds, maxSteps=1, cellSize=0.4):
    geometry, grid = init(file, cellSize)
    create_peds(numPeds, geometry, grid)
    # peds = {}
    # peds[0] = ped
    # print(peds[0] = ped)
    # plot_geometry_grid(geometry, grid)
    # init_static_ff(geometry, grid)

    doorDistance = compute_door_distance(geometry, grid)
    plot_prob_field(geometry, grid, doorDistance)
    # plot_geometry_peds(geometry, grid, geometry.peds)
    # foo = get_neighbors(geometry, grid, [10, 20])
    # plot_marked_zells(geometry, grid, foo)
