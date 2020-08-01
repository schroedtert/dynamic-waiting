from geometry import Geometry
from grid import Grid

from numpy.random import choice
from simulation_parameters import SimulationParameters

from floorfield import *
from plotting import *


class CA:
    static_ff = None
    simulation_parameters: SimulationParameters

    def __init__(self, simulation_parameters: SimulationParameters, geometry: Geometry, grid: Grid):
        self.simulation_parameters = simulation_parameters
        self.static_ff = compute_static_ff(geometry, grid, self.simulation_parameters)

    def compute_step(self, geometry: Geometry, grid: Grid):
        next_step = {}
        for ped_id, ped in geometry.pedestrians.items():
            individual_ff = compute_individual_ff(geometry, grid, ped, self.simulation_parameters)
            combined = compute_overall_ff(geometry, grid, self.static_ff, individual_ff)

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
