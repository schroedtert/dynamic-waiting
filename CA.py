from geometry import Geometry
from grid import Grid

from numpy.random import choice

from floorfield import *
from plotting import *

class CA:
    staticFF = None

    def __init__(self, geometry: Geometry, grid: Grid):
        self.staticFF = compute_static_ff(geometry, grid)

    def compute_step(self, geometry: Geometry, grid: Grid):
        next_step = {}
        for ped_id, ped in geometry.pedestrians.items():
            dynamicFF = compute_dynamic_ff(geometry, grid, ped)
            filterFF = compute_filter_ff(geometry, grid, ped)
            combined = compute_overall_ff(geometry, grid, self.staticFF, dynamicFF, filterFF)

            prob_neighbor = compute_prob_neighbors(geometry, grid, ped, combined)
            next_step[ped_id] = self.compute_next_step(prob_neighbor, geometry, grid, ped_id)

        self.apply_step(geometry, grid, next_step)

        return

    @staticmethod
    def compute_next_step(prob, geometry, grid, key):
        keys = list(prob.keys())
        probs = list(prob.values())

        return choice(keys, 1, p=probs)

    @staticmethod
    def apply_step(geometry: Geometry, grid: Grid, next_step):
        # TODO collision detection
        for key, step in next_step.items():
            neighbors = grid.get_neighbors(geometry, geometry.pedestrians[key].pos)
            geometry.pedestrians[key].set_pos(neighbors[step[0]])
