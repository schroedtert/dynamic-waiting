import logging

from simulation_parameters import SimulationParameters
from CA import CA
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian
from plotting import *
from trajectory import Trajectory
from constants import *
from IO import create_output_directory, save_floor_field

import random

logfile = 'log.dat'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init(file):
    geometry = Geometry(file)
    grid = Grid(geometry)
    return geometry, grid


def create_peds(num_peds: int, standing_peds: int, geometry: Geometry, grid: Grid):
    for index in range(num_peds):
        while True:
            i = random.randint(0, grid.gridX.shape[0] - 1)
            j = random.randint(0, grid.gridY.shape[1] - 1)

            occupied = False
            for ped in geometry.pedestrians.values():
                if ped.i() == i and ped.j() == j:
                    occupied = True
                    break

            if not occupied and grid.inside_cells[i][j] == 1:
                geometry.pedestrians[index] = Pedestrian([i, j], Neighbors.left, index, False)
                break

    keys = random.sample(list(geometry.pedestrians), standing_peds)
    for key in keys:
        geometry.pedestrians[key].standing = True


def add_pedestrian(geometry: Geometry, grid: Grid):
    entrances = grid.entrance_cells
    entrance_cells = np.transpose(np.where(entrances == 1))

    ped_cells = np.zeros(shape=(len(geometry.pedestrians.items()) + 1, 2))

    for i in range(len(geometry.pedestrians.items())):
        ped = geometry.pedestrians[i]
        ped_cells[i] = [ped.i(), ped.j()]

    ped_cells[len(geometry.pedestrians.items())] = [41, 9]

    exclude_cells = (entrance_cells[:, None] == ped_cells).all(-1).any(-1)
    entrance_cells = entrance_cells[exclude_cells == False]

    cell = random.choice(entrance_cells)
    max_id = max(geometry.pedestrians)
    id = max_id + 1
    geometry.pedestrians[id] = Pedestrian([cell[0], cell[1]], Neighbors.left, id, False)


def run_simulation(simulation_parameters: SimulationParameters):
    create_output_directory(simulation_parameters.output_path)

    file = open(simulation_parameters.file, 'r')
    random.seed(simulation_parameters.seed)

    geometry, grid = init(file)

    create_peds(simulation_parameters.init_agents,
                simulation_parameters.standing_agents,
                geometry, grid)

    if simulation_parameters.plot:
        plot_geometry_peds(geometry, grid, geometry.pedestrians)

    ca = CA(simulation_parameters, geometry, grid)

    # Save simulation parameters and static ff
    ca.save(simulation_parameters.output_path)
    simulation_parameters.write_to_file(simulation_parameters.output_path)

    traj = Trajectory(grid, simulation_parameters.steps)

    for step in range(simulation_parameters.steps):
        print("========================= step {:2d} ======================================".format(step))
        if len(geometry.pedestrians.values()) < simulation_parameters.max_agents and step % 10 == 0:
            add_pedestrian(geometry, grid)

        ca.compute_step(geometry, grid)
        traj.add_step(step, grid, geometry.pedestrians)
        if simulation_parameters.plot:
            plot_geometry_peds(geometry, grid, geometry.pedestrians)

    print("========================= done ======================================")

    if simulation_parameters.plot:
        plot_trajectories(geometry, grid, traj, geometry.pedestrians)
        plot_space_usage(geometry, grid, traj, simulation_parameters.steps)

    traj.save(simulation_parameters.output_path)
