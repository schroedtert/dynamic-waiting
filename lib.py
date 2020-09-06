import logging
import os
import random
import time

from CA import CA
from IO import create_output_directory
from constants import *
from plotting import *
from simulation_parameters import SimulationParameters
from trajectory import Trajectory
import random
import numpy as np


def init(file):
    """
    Inits simulation context (used for parallel computations)
    :param file: file containing geometry
    :return: geometry and grid for simulation
    """
    geometry = Geometry(file)
    grid = Grid(geometry)
    return geometry, grid


def create_peds(simulation_parameters: SimulationParameters, geometry: Geometry, grid: Grid):
    """
    Creates the initial pedestrians in the simulation
    :param simulation_parameters: parameters for simulation
    :param geometry: geometry to use
    :param grid: grid to use
    """
    for index in range(simulation_parameters.init_agents):
        while True:
            i = random.randint(0, grid.gridX.shape[0] - 1)
            j = random.randint(0, grid.gridY.shape[1] - 1)

            if grid.inside_cells[i][j] == 1:
                occupied = False
                for ped in geometry.pedestrians.values():
                    if ped.i() == i and ped.j() == j:
                        occupied = True
                        break

                if not occupied:
                    exits = [0, 1]
                    exit_id = np.random.choice(exits, 1, p=simulation_parameters.exit_prob)[0]

                    geometry.pedestrians[index] = Pedestrian([i, j], Neighbors.left, index, False, exit_id)
                    break

    keys = random.sample(list(geometry.pedestrians), simulation_parameters.standing_agents)
    for key in keys:
        geometry.pedestrians[key].standing = True


def add_pedestrian(simulation_parameters: SimulationParameters, geometry: Geometry, grid: Grid, step: int):
    """
    Add pedestrian at entrances depending on flow to the simulation
    :param simulation_parameters: parameters of simulation
    :param geometry: geometry to use
    :param grid: grid to use
    :param step: current time step
    """
    for key in geometry.entrances.keys():
        entrance_properties = geometry.entrances_properties[key]
        if step % entrance_properties[0] == 0:
            for i in range(geometry.entrances_properties[key][1]):
                entrances = grid.door_cells[key]
                entrance_cells = np.transpose(np.where(entrances == 1))

                ped_cells = np.zeros(shape=(len(geometry.pedestrians.items()) + 1, 2))

                for i in range(len(geometry.pedestrians.items())):
                    ped = geometry.pedestrians[i]
                    ped_cells[i] = [ped.i(), ped.j()]

                ped_cells[len(geometry.pedestrians.items())] = [41, 9]

                exclude_cells = (entrance_cells[:, None] == ped_cells).all(-1).any(-1)
                entrance_cells = entrance_cells[exclude_cells == False]

                cell = random.choice(entrance_cells)
                max_id = 0
                if len(geometry.pedestrians.items()) != 0:
                    max_id = max(geometry.pedestrians) + 1

                id = max_id
                exits = [0, 1]
                exit_id = np.random.choice(exits, 1, p=simulation_parameters.exit_prob)[0]

                geometry.pedestrians[id] = Pedestrian([cell[0], cell[1]], Neighbors.left, id, False, exit_id)


def run_simulation(simulation_parameters: SimulationParameters):
    """
    Runs the simulation with the given parameters
    :param simulation_parameters: parameters of simulation
    :return:
    """
    create_output_directory(simulation_parameters.output_path)
    file = open(simulation_parameters.file, 'r')
    random.seed(simulation_parameters.seed)

    geometry, grid = init(file)

    create_peds(simulation_parameters, geometry, grid)

    if simulation_parameters.plot:
        plot_geometry_peds(geometry, grid, geometry.pedestrians)

    ca = CA(simulation_parameters, geometry, grid)

    # Save simulation parameters and static ff
    ca.save(simulation_parameters.output_path)
    simulation_parameters.write_to_file(simulation_parameters.output_path)

    traj = Trajectory(grid, simulation_parameters.steps)

    for step in range(simulation_parameters.steps):
        start_time = time.time()
        if len(geometry.pedestrians.values()) < simulation_parameters.max_agents:
            add_pedestrian(simulation_parameters, geometry, grid, step)

        ca.compute_step(geometry, grid)
        traj.add_step(step, grid, geometry.pedestrians, simulation_parameters.output_path)
        end_time = time.time()
        print("Process {} finished step {:3d}/{:3d} in {:4.5f}s".format(os.getpid(), step + 1, simulation_parameters.steps,
                                                                end_time - start_time))
    traj.save(simulation_parameters.output_path)
    return
