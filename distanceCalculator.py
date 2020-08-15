import skfmm

from IO import *
from geometry import Geometry
from grid import Grid

from plotting import *


def compute_distance_fmm(geometry: Geometry, grid: Grid, start, mask, speed=None):
    inside = grid.inside_cells

    phi = inside - 5 * start
    phi = np.ma.MaskedArray(phi, mask)

    if speed is None:
        distance = skfmm.distance(phi, dx=grid.cellsize)
    else:
        distance = skfmm.travel_time(phi, speed, dx=grid.cellsize)

    return distance


def compute_entrance_distance(geometry: Geometry, grid: Grid):
    entrances = grid.entrance_cells
    # plot_prob_field(geometry, grid, entrances)
    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, entrances != 1)

    # plot_prob_field(geometry, grid, np.ma.MaskedArray(entrances, mask))

    # speed = 0.5 * np.ones_like(grid.gridX)

    # for entrance in geometry.entrances.values():
    #     y_min = entrance.bbox().ymin()
    #     y_max = entrance.bbox().ymax()
    #
    #     x_min = entrance.bbox().xmin()
    #
    #     speed_mask_y = np.logical_and(grid.gridY >= y_min + 1000, grid.gridY <= y_max - 1000)
    #     speed_mask_x = np.logical_and(grid.gridX >= x_min - 5000, grid.gridX <= x_min + 5000)
    #     speed_mask = np.logical_and(speed_mask_x, speed_mask_y)
    #     speed[speed_mask] = 5

    return compute_distance_fmm(geometry, grid, entrances, mask)


def compute_exit_distance(geometry: Geometry, grid: Grid):
    exits = grid.get_exit_cells(geometry)
    wall = grid.get_wall_cells(geometry)

    exits[wall == 1] = 0

    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, exits != 1)

    mask_inside = grid.inside_cells == 0
    return np.ma.MaskedArray(compute_distance_fmm(geometry, grid, exits, mask), mask_inside)


def compute_wall_distance(geometry: Geometry, grid: Grid):
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
    peds = grid.get_ped_cells(geometry, ped)

    outside = grid.outside_cells
    mask = outside == 1

    return compute_distance_fmm(geometry, grid, peds, mask)


def compute_attraction_ground_distance(geometry: Geometry, grid: Grid):
    attraction_ground = grid.get_attraction_ground_cells(geometry)

    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, attraction_ground != 1)

    return compute_distance_fmm(geometry, grid, attraction_ground, mask)


def compute_attraction_mounted_distance(geometry: Geometry, grid: Grid):
    attraction_mounted = grid.get_attraction_mounted_cells(geometry)

    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, attraction_mounted != 1)

    speed = 0.2 * np.ones_like(grid.gridX)

    for attraction in geometry.attraction_mounted.values():
        y_min = attraction.bounds[1]
        y_max = attraction.bounds[3]

        speed_mask = np.logical_and(grid.gridY >= y_min, grid.gridY <= y_max)
        speed[speed_mask] = 2

    return compute_distance_fmm(geometry, grid, attraction_mounted, mask, speed)


def compute_point_distance(geometry: Geometry, grid: Grid, cell: [int, int]):
    entrances = grid.entrance_cells
    outside = grid.outside_cells
    mask = np.logical_and(outside == 1, entrances != 1)

    x0 = grid.gridX[cell[0]][cell[1]]
    y0 = grid.gridY[cell[0]][cell[1]]

    distance = np.sqrt((grid.gridX - x0) ** 2 + (grid.gridY - y0) ** 2)

    distance = np.ma.MaskedArray(distance, mask)
    return distance
