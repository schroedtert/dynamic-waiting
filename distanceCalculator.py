import skfmm

from IO import *
from geometry import Geometry
from grid import Grid

from plotting import *


def compute_distance_fmm(geometry: Geometry, grid: Grid, start, with_peds=False):
    # phi = -1 * np.ones_like(grid.gridX)

    inside = grid.get_inside_cells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), inside))

    outside = grid.get_outside_cells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), outside))

    # doors = grid.get_entrance_cells(geometry)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), doors))

    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), peds))

    phi = inside - start
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), phi))

    mask = np.logical_and(outside == 1, start != 1)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), mask))

    # mask = np.logical_and(mask, doors != 1)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), mask))

    if with_peds:
        peds = grid.get_ped_cells(geometry)
        mask = np.logical_or(mask, peds == 1)
    # plot_prob_field(geometry, grid, np.ma.MaskedArray(np.ones_like(grid.gridX), mask))

    phi = np.ma.MaskedArray(phi, mask)
    # plot_prob_field(geometry, grid, phi)
    distance = skfmm.distance(phi, dx=grid.cellsize)
    return distance


def compute_entrance_distance(geometry: Geometry, grid: Grid):
    entrances = grid.get_entrance_cells(geometry)

    return compute_distance_fmm(geometry, grid, entrances)


def compute_exit_distance(geometry: Geometry, grid: Grid):
    exits = grid.get_exit_cells(geometry)

    return compute_distance_fmm(geometry, grid, exits)


def compute_wall_distance(geometry: Geometry, grid: Grid):
    wall = grid.get_wall_cells(geometry)
    edges = grid.get_edge_cells(geometry)
    wall = wall - edges
    return compute_distance_fmm(geometry, grid, wall)


def compute_ped_distance(geometry: Geometry, grid: Grid, ped: Pedestrian = None):
    peds = grid.get_ped_cells(geometry, ped)

    return compute_distance_fmm(geometry, grid, peds, False)


def compute_edge_distance(geometry: Geometry, grid: Grid):
    danger = grid.get_danger_cells(geometry)
    return compute_distance_fmm(geometry, grid, danger)
    # return danger
