import random

from distanceCalculator import compute_ped_distance, compute_door_distance, compute_wall_distance
from geometry import Geometry
from grid import Grid
from plotting import plot_prob_field

moore = False


def compute_static_ff(geometry: Geometry, grid: Grid):
    doorDistance = compute_door_distance(geometry, grid)
    plot_prob_field(geometry, grid, doorDistance)

    wallDistance = compute_wall_distance(geometry, grid)
    plot_prob_field(geometry, grid, wallDistance)

    # staticFF = np.empty(grid.gridY.shape)
    # staticFF = np.sqrt(grid.gridX.shape[0] ** 2 + grid.gridX.shape[1])

    return


def compute_dynamic_ff(geometry: Geometry, grid: Grid):
    pedDistance = compute_ped_distance(geometry, grid)
    plot_prob_field(geometry, grid, pedDistance)

    return


def init_dynamic_ff():
    return


def compute_dynamic_ff():
    return


def get_neighbors(geometry: Geometry, grid: Grid, cell: [int, int]):
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
