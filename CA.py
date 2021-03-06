from numpy.random import choice

from floorfield import *
from plotting import *
from IO import save_floor_field


class CA:
    """ Simulator for waiting pedestrians with a CA.

    :param static_ff: The underlying static floor field for all pedestrians
    :param simulation_parameters: The used simulation parameters (see class:SimulationParameters)
    """
    static_ff = None
    simulation_parameters: SimulationParameters

    def __init__(self, simulation_parameters: SimulationParameters, geometry: Geometry, grid: Grid):
        """
        Init the CA.
        :param simulation_parameters: simulation parameters to use
        :param geometry: geometry to use
        :param grid: grid to use
        """
        self.simulation_parameters = simulation_parameters
        self.static_ff = compute_static_ff(geometry, grid, self.simulation_parameters)

    def compute_step(self, geometry: Geometry, grid: Grid):
        """
        Computes one time step of the simulations.
        :param geometry: geometry to use
        :param grid: grid to use
        """
        next_step = {}
        prob_next_step = {}
        for ped_id, ped in geometry.pedestrians.items():
            if ped.standing:
                next_step[ped_id] = [Neighbors.self]
            else:
                individual_ff = compute_individual_ff(geometry, grid, ped, self.simulation_parameters)
                combined = compute_overall_ff(geometry, grid, self.static_ff[ped.exit_id], individual_ff)

                prob_neighbor = compute_prob_neighbors(geometry, grid, ped, combined, self.simulation_parameters.w_direction)
                step = self.compute_next_step(prob_neighbor)

                next_step[ped_id] = step
                prob_next_step[ped_id] = prob_neighbor[step]

        self.apply_step(geometry, grid, next_step, prob_next_step)

    @staticmethod
    def compute_next_step(prob):
        """
        Chooses the next step based on *prob*.
        :param prob: Probabilities for the corresponding neighboring fields
        :return: Next step
        """
        keys = list(prob.keys())
        probs = list(prob.values())

        return choice(keys, 1, p=probs)[0]

    @staticmethod
    def apply_step(geometry: Geometry, grid: Grid, next_step, prob_next_step):
        """
        Applies the current step to pedestrians and resolves occurring conflicts.
        :param geometry: geometry to use
        :param grid: grid to use
        :param next_step: next steps of all pedestrians
        :param prob_next_step: probabilities of next steps
        """
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
        """
        Solves occurring conflicts by using relative probabilities
        :param geometry: geometry to use
        :param targets: target fields for each pedestrian
        :param next_step: targeted field for each pedestrian
        :param prob_next_step: probabilities of each targeted field
        :param conflicts: conflicting targets
        :return:
        """
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
        """
        Finds conflicts the *targets*, checks if two or more pedestrians target the same cell.
        :param targets: Targeted cells
        :return: Conflicting target cells
        """
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
        """
        Saves the underlying static floor field.
        :param output_path:
        :return:
        """
        for id, ff in self.static_ff.items():
            save_floor_field(ff, output_path, 'static_ff_{}.txt'.format(id))
