import skfmm

from IO import *
from geometry import Geometry
from grid import Grid

from plotting import *

def compute_distance_fmm(geometry: Geometry, grid: Grid, start, with_peds=True):
    # phi = -1 * np.ones_like(grid.gridX)

    inside = grid.getInsideCells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), inside))

    outside = grid.getOutsideCells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), outside))

    doors = grid.getDoorCells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), doors))

    peds = grid.getPedCells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), peds))

    phi = inside - start
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), phi))

    mask = np.logical_and(outside == 1, start != 1)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), mask))

    mask = np.logical_and(mask, doors != 1)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), mask))

    if with_peds:
        mask = np.logical_or(mask, peds == 1)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), mask))

    phi = np.ma.MaskedArray(phi, mask)
    # plot_prob_field(geometry, grid, phi)
    distance = skfmm.distance(phi, dx=grid.cellsize)
    return distance


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


def compute_edge_distance(geometry: Geometry, grid: Grid):
    danger = grid.getDangerCells(geometry)
    return compute_distance_fmm(geometry, grid, danger)
    # return danger
