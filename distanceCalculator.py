import skfmm

from IO import *
from geometry import Geometry
from grid import Grid


def compute_distance_fmm(geometry: Geometry, grid: Grid, start, with_peds=True):
    # phi = -1 * np.ones_like(grid.gridX)

    inside = grid.getInsideCells(geometry)
    outside = grid.getOutsideCells(geometry)
    doors = grid.getDoorCells(geometry)
    peds = grid.getPedCells(geometry)
    phi = inside - start
    mask = np.logical_and(outside == 1, start != 1)
    mask = np.logical_and(mask, doors != 1)
    if with_peds:
        mask = np.logical_or(mask, peds == 1)
    phi = np.ma.MaskedArray(phi, mask)
    distance = skfmm.distance(phi, dx=grid.cellsize)
    return np.ma.filled(distance, np.inf)


def compute_door_distance(geometry: Geometry, grid: Grid):
    doors = grid.getDoorCells(geometry)

    return compute_distance_fmm(geometry, grid, doors)


def compute_wall_distance(geometry: Geometry, grid: Grid):
    wall = grid.getWallCells(geometry)
    edges = grid.getEdgeCells(geometry)
    wall = wall - edges
    return compute_distance_fmm(geometry, grid, wall)


def compute_ped_distance(geometry: Geometry, grid: Grid):
    peds = grid.getPedCells(geometry)
    return compute_distance_fmm(geometry, grid, peds, False)


def compute_danger_distance(geometry: Geometry, grid: Grid):
    danger = grid.getDangerCells(geometry)
    return compute_distance_fmm(geometry, grid, danger)
