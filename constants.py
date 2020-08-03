from enum import Enum

MTOMM = 1000
CELLSIZE = 0.5 * MTOMM
THRESHOLD = 0.5 * CELLSIZE


class Neighbors(Enum):
    self = 0
    left = 1
    top = 2
    right = 3
    bottom = 4


class Direction(Enum):
    stay = 0
    left = 1
    forward = 2
    right = 3
    back = 4


weighted_direction = {
    Direction.stay: 0.2,
    Direction.left: 0.15,
    Direction.forward: 0.45,
    Direction.right: 0.15,
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
