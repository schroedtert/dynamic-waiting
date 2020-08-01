import logging
import random

from CA import CA
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian
from plotting import *
from trajectory import Trajectory
from constants import *

logfile = 'log.dat'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init(file):
    geometry = Geometry(file)
    grid = Grid(geometry)
    return geometry, grid


def create_peds(num_peds: int, geometry: Geometry, grid: Grid):
    for index in range(num_peds):
        while True:
            i = random.randint(0, grid.gridX.shape[0] - 1)
            j = random.randint(0, grid.gridY.shape[1] - 1)
            # i = 11
            # j = 2
            occupied = False
            for id, ped in geometry.pedestrians.items():
                if ped.i() == i and ped.j() == j:
                    occupied = True
                    break

            x, y = grid.get_coordinates(i, j)
            if not occupied and geometry.is_in_geometry(x, y):
                geometry.pedestrians[index] = Pedestrian([i, j], Neighbors.left, index)
                break


def run_simulation(file, num_peds=5, max_steps=50):
    geometry, grid = init(file)
    create_peds(num_peds, geometry, grid)

    ca = CA(geometry, grid)
    plot_geometry_peds(geometry, grid, geometry.pedestrians)
    traj = Trajectory()
    for step in range(max_steps):
        print("========================= step {:2d} ======================================".format(step))
        ca.compute_step(geometry, grid)
        # plot_geometry_peds(geometry, grid, geometry.peds)
        traj.add_step(step, grid, geometry.pedestrians)

    plot_trajectories(geometry, grid, traj, geometry.pedestrians)
    # plot_geometry_peds(geometry, grid, geometry.peds)
    print("========================= done ======================================".format(step))
