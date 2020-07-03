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
from geometry import Geometry
from grid import Grid
import skfmm
import plotting as plot

from pedestrian import Pedestrian

from pedestrian import Pedestrian

logfile = 'log.dat'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init(file, cellSize):
    geometry = Geometry(file)
    grid = Grid(geometry, cellSize)
    # grid = create_grid(geometry, cellSize)
    return geometry, grid


def create_peds(numPeds: int, geometry: Geometry, grid:Grid):

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

def compute_distance_fmm(geometry: Geometry, grid: Grid, start):
    phi = -1 * np.ones_like(grid.gridX)

    inside = grid.getInsideCells(geometry)
    outside = grid.getOutsideCells(geometry)
    doors = grid.getDoorCells(geometry)

    phi = inside - start
    mask = np.logical_and(outside == 1, start != 1)
    mask = np.logical_and(mask, doors != 1)
    phi = np.ma.MaskedArray(phi, mask)
    d = skfmm.distance(phi, dx=grid.cellsize)

    return d

def compute_door_distance(geometry: Geometry, grid: Grid):
    doors = grid.getDoorCells(geometry)

    return compute_distance_fmm(geometry, grid, doors)

def compute_wall_distance(geometry: Geometry, grid: Grid):
    wall = grid.getWallCells(geometry)

    return compute_distance_fmm(geometry, grid, wall)


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
        x, y = grid.getCoordinates(posNeighbor[0], posNeighbor[1])
        if geometry.isInGeometry(x, y):
            neighbors.append(posNeighbor)

    # not shuffling significantly alters the simulation...
    random.shuffle(neighbors)
    return neighbors

def run_simulation(file, numPeds, maxSteps=1, cellSize=0.4):
    geometry, grid = init(file, cellSize)
    # create_peds(numPeds, geometry, grid)
    # plot.plot_voronoi_peds(geometry, grid, geometry.peds)
    # plot.plot_geometry_peds(geometry, grid, geometry.peds)


    # peds = {}
    # peds[0] = ped
    # print(peds[0] = ped)
    # plot_geometry_grid(geometry, grid)
    # init_static_ff(geometry, grid)

    doorDistance = compute_door_distance(geometry, grid)
    plot.plot_prob_field(geometry, grid, doorDistance)

    wallDistance = compute_wall_distance(geometry, grid)
    plot.plot_prob_field(geometry, grid, wallDistance)

    # plot_prob_field(geometry, grid, doorDistance)
    # plot_geometry_peds(geometry, grid, geometry.peds)
    # foo = get_neighbors(geometry, grid, [10, 20])
    # plot_marked_zells(geometry, grid, foo)
