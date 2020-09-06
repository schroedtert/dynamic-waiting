from enum import Enum

MTOMM = 1000
"""Factor to scale from meter to millimeter."""

CELLSIZE = 0.5 * MTOMM
"""Cell size for CA."""

THRESHOLD = 0.5 * CELLSIZE
"""Threshold for checking if a cell belongs to some structure."""


class Neighbors(Enum):
    """
    Neighbors of current cell and the corresponding indices.
    """
    self = 0
    left = 1
    top = 2
    right = 3
    bottom = 4


class Direction(Enum):
    """
    Direction the pedestrian has moved.
    """
    stay = 0
    left = 1
    forward = 2
    right = 3
    back = 4


weighted_direction = {
    Direction.stay: 0.25,
    Direction.left: 0.10,
    Direction.forward: 0.50,
    Direction.right: 0.10,
    Direction.back: 0.05
}

weighted_neighbors = {
    Neighbors.self: {Neighbors.self: 0.4,
                     Neighbors.left: 0.15,
                     Neighbors.top: 0.15,
                     Neighbors.right: 0.15,
                     Neighbors.bottom: 0.15},
    Neighbors.left: {Neighbors.self: weighted_direction[Direction.stay],
                     Neighbors.left: weighted_direction[Direction.forward],
                     Neighbors.top: weighted_direction[Direction.right],
                     Neighbors.right: weighted_direction[Direction.back],
                     Neighbors.bottom: weighted_direction[Direction.left]},
    Neighbors.top: {Neighbors.self: weighted_direction[Direction.stay],
                    Neighbors.left: weighted_direction[Direction.left],
                    Neighbors.top: weighted_direction[Direction.forward],
                    Neighbors.right: weighted_direction[Direction.right],
                    Neighbors.bottom: weighted_direction[Direction.back]},
    Neighbors.right: {Neighbors.self: weighted_direction[Direction.stay],
                      Neighbors.left: weighted_direction[Direction.back],
                      Neighbors.top: weighted_direction[Direction.left],
                      Neighbors.right: weighted_direction[Direction.forward],
                      Neighbors.bottom: weighted_direction[Direction.right]},
    Neighbors.bottom: {Neighbors.self: weighted_direction[Direction.stay],
                       Neighbors.left: weighted_direction[Direction.right],
                       Neighbors.top: weighted_direction[Direction.back],
                       Neighbors.right: weighted_direction[Direction.left],
                       Neighbors.bottom: weighted_direction[Direction.forward]}
}