from geometry import Geometry
from geometry import Geometry
from grid import Grid

from numpy.random import choice

from floorfield import *


class CA:
    staticFF = None

    def __init__(self, geometry: Geometry, grid: Grid):
        self.staticFF = compute_static_ff(geometry, grid)

    def compute_step(self, geometry: Geometry, grid: Grid):
        dynamicFF = compute_dynamic_ff(geometry, grid)
        filterFF = compute_filter_ff(geometry, grid)
        combined = compute_overall_ff(geometry, grid, self.staticFF, dynamicFF, filterFF)

        next_step = {}
        for key, ped in geometry.peds.items():
            prob_neighbor = compute_prob_neighbors(geometry, grid, ped, combined)
            next_step[key] = self.compute_next_step(ped, prob_neighbor)
            self.apply_step(geometry, grid, next_step)
        return

    def compute_next_step(self, ped: Pedestrian, prob):
        keys = list(prob.keys())
        probs = list(prob.values())

        draw = choice(keys, 1, p=probs)
        return draw

    def apply_step(self, geometry: Geometry, grid: Grid, next_step):
        # TODO collision detection
        for key, step in next_step.items():
            neighbors = grid.getNeighbors(geometry, geometry.peds[key].pos)
            geometry.peds[key].pos = neighbors[step[0]]
