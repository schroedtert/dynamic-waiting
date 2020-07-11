import logging
import random

from CA import CA
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian
from plotting import *
from trajectory import Trajectory

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
            occupied = False
            for id, ped in geometry.peds.items():
                if ped.i() == i and ped.j() == j:
                    occupied = True
                    break

            x, y = grid.get_coordinates(i, j)
            if not occupied and geometry.is_in_geometry(x, y):
                geometry.peds[index] = Pedestrian([i, j])
                # print("{:02d} {:5.2f} {:5.2f}".format(index, x, y))
                break


def run_simulation(file, num_peds, max_steps=10):
    geometry, grid = init(file)
    create_peds(num_peds, geometry, grid)

    ca = CA(geometry, grid)

    traj = Trajectory()
    for step in range(max_steps):
        ca.compute_step(geometry, grid)
        # plot_geometry_peds(geometry, grid, geometry.peds)
        traj.add_step(step, grid, geometry.peds)

    plot_trajectories(geometry, grid, traj)
    # plot.plot_voronoi_peds(geometry, grid, geometry.peds)
    # plot.plot_geometry_peds(geometry, grid, geometry.peds)

    # peds = {}
    # peds[0] = ped
    # print(peds[0] = ped)
    # plot_geometry_grid(geometry, grid)
    # init_static_ff(geometry, grid)

    # plot_prob_field(geometry, grid, doorDistance)
    # plot_geometry_peds(geometry, grid, geometry.peds)
    # foo = get_neighbors(geometry, grid, [10, 20])
    # plot_marked_zells(geometry, grid, foo)
