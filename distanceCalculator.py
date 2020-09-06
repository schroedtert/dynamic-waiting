import skfmm

from IO import *
from geometry import Geometry
from grid import Grid

from plotting import *


def compute_distance_fmm(geometry: Geometry, grid: Grid, start, mask, speed=None):
    """
    Compute the distance to start in geometry.
    :param geometry: Geometry to use
    :param grid: Grid to use
    :param start: start cells
    :param mask: masked cells
    :param speed: speed field
    :return: distance to start by ffm
    """
    inside = grid.inside_cells

    phi = inside - 5 * start
    phi = np.ma.MaskedArray(phi, mask)

    if speed is None:
        distance = skfmm.distance(phi, dx=grid.cellsize)
    else:
        distance = skfmm.travel_time(phi, speed, dx=grid.cellsize)

    return distance


def compute_entrance_distance(geometry: Geometry, grid: Grid):
    """
    Compute the distance to the entrances.
    :param geometry: Geometry to use
    :param grid: Grid to use
    :return: Distance field to entrance
    """
    entrances = grid.entrance_cells
    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, entrances != 1)

    return compute_distance_fmm(geometry, grid, entrances, mask)


def compute_exit_distance(geometry: Geometry, grid: Grid, exit_id: int):
    """
    Compute the distance to the exit with exit_id.
    :param geometry: Geometry to use
    :param grid: Grid to use
    :param exit_id: Exit id
    :return: Distance field to specific exit
    """

    exits = grid.exit_cells[exit_id]
    wall = grid.get_wall_cells(geometry)

    exits[wall == 1] = 0

    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, exits != 1)

    mask_inside = grid.inside_cells == 0
    return np.ma.MaskedArray(compute_distance_fmm(geometry, grid, exits, mask), mask_inside)


def compute_wall_distance(geometry: Geometry, grid: Grid):
    """
    Compute the distance to the walls.
    :param geometry: Geometry to use
    :param grid: Grid to use
    :return: Distance field to walls
    """

    wall = grid.get_wall_cells(geometry)
    entrances = grid.entrance_cells
    edges = grid.get_edge_cells(geometry)
    wall[edges == 1] = 0
    wall[entrances == 1] = 0

    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, wall != 1)

    distance = compute_distance_fmm(geometry, grid, wall, mask)
    return np.ma.MaskedArray(distance, outside == 1)


def compute_ped_distance(geometry: Geometry, grid: Grid, ped: Pedestrian = None):
    """
    Compute the distance to the pedestrians excluding ped.
    :param geometry: Geometry to use
    :param grid: Grid to use
    :param ped: Pedestrian to ignorte
    :return: Distance field to entrance
    """

    peds = grid.get_ped_cells(geometry, ped)
    outside = grid.outside_cells
    mask = outside == 1

    return compute_distance_fmm(geometry, grid, peds, mask)


def compute_point_distance(geometry: Geometry, grid: Grid, cell: [int, int]):
    """
    Comp
    :param geometry:
    :param grid:
    :param cell:
    :return:
    """
    entrances = grid.entrance_cells
    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, entrances != 1)

    x0 = grid.gridX[cell[0]][cell[1]]
    y0 = grid.gridY[cell[0]][cell[1]]

    distance = np.sqrt((grid.gridX - x0) ** 2 + (grid.gridY - y0) ** 2)

    distance = np.ma.MaskedArray(distance, mask)
    return distance
