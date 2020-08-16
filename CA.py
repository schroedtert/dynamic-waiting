from numpy.random import choice

from floorfield import *
from floorfield import compute_prob_neighbors
from plotting import *
from IO import save_floor_field

class CA:
    static_ff = None
    simulation_parameters: SimulationParameters

    def __init__(self, simulation_parameters: SimulationParameters, geometry: Geometry, grid: Grid):
        self.simulation_parameters = simulation_parameters
        self.static_ff = compute_static_ff(geometry, grid, self.simulation_parameters)

    def compute_step(self, geometry: Geometry, grid: Grid):
        next_step = {}
        prob_next_step = {}
        for ped_id, ped in geometry.pedestrians.items():
            if ped.standing:
                next_step[ped_id] = [Neighbors.self]
            else:
                individual_ff = compute_individual_ff(geometry, grid, ped, self.simulation_parameters)
                combined = compute_overall_ff(geometry, grid, self.static_ff[ped.exit_id], individual_ff)

                prob_neighbor = compute_prob_neighbors(geometry, grid, ped, combined,
                                                       self.simulation_parameters.w_direction)
                step = self.compute_next_step(prob_neighbor)

                next_step[ped_id] = step
                prob_next_step[ped_id] = prob_neighbor[step]

        self.apply_step(geometry, grid, next_step, prob_next_step)

        return

    @staticmethod
    def compute_next_step(prob):
        keys = list(prob.keys())
        probs = list(prob.values())

        return choice(keys, 1, p=probs)[0]

    @staticmethod
    def apply_step(geometry: Geometry, grid: Grid, next_step, prob_next_step):
        targets = {}
        for key, step in next_step.items():
            neighbors = grid.get_neighbors(geometry, geometry.pedestrians[key].pos)
            targets[key] = neighbors[step]

        conflicts = CA.find_conflicts(targets)
        CA.solve_conflicts(geometry, targets, next_step, prob_next_step, conflicts)

        for key, target in targets.items():
            geometry.pedestrians[key].set_pos(target)

    @staticmethod
    def solve_conflicts(geometry: Geometry, targets, next_step, prob_next_step, conflicts):
        for conflict in conflicts:
            probs = []
            for ped_id in conflict:
                if next_step[ped_id] == Neighbors.self:
                    probs.append(1000000)
                else:
                    probs.append(prob_next_step[ped_id])
            probs = [x / sum(probs) for x in probs]
            c = choice(conflict, 1, p=probs)[0]

            for ped_id in conflict:
                if ped_id != c:
                    targets[ped_id] = [geometry.pedestrians[ped_id].i(), geometry.pedestrians[ped_id].j()]

    @staticmethod
    def find_conflicts(targets):
        targets_list = list(targets.values())
        duplicates = []
        for key, target in targets.items():
            if targets_list.count(target) > 1:
                if duplicates.count(target) == 0:
                    duplicates.append(target)

        conflicts = []
        for duplicate in duplicates:
            indices = [i for i, x in enumerate(targets_list) if x == duplicate]
            conflicts.append(indices)

        return conflicts

    def save(self, output_path):
        for id, ff in self.static_ff.items():
            save_floor_field(ff, output_path, 'static_ff_{}.txt'.format(id))
