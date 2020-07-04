import logging
import random

from CA import CA
from geometry import Geometry
from grid import Grid
from pedestrian import Pedestrian

logfile = 'log.dat'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init(file, cellSize):
    geometry = Geometry(file)
    grid = Grid(geometry, cellSize)
    return geometry, grid


def create_peds(numPeds: int, geometry: Geometry, grid: Grid):
    for index in range(numPeds):
        while True:
            i = random.randint(0, grid.gridX.shape[0] - 1)
            j = random.randint(0, grid.gridY.shape[1] - 1)
            occupied = False
            for id, ped in geometry.peds.items():
                if ped.i() == i and ped.j() == j:
                    occupied = True
                    break

            x, y = grid.getCoordinates(i, j)
            if not occupied and geometry.isInGeometry(x, y):
                geometry.peds[index] = Pedestrian([i, j])
                # print("{:02d} {:5.2f} {:5.2f}".format(index, x, y))
                break


def run_simulation(file, numPeds, maxSteps=1, cellSize=0.4):
    geometry, grid = init(file, cellSize)
    create_peds(numPeds, geometry, grid)

    for key, ped in geometry.peds.items():
        x, y = grid.getCoordinates(ped.i(), ped.j())
        geometry.visibleArea(x, y)

    ca = CA(geometry, grid)
    for step in range(maxSteps):
        ca.compute_step(geometry, grid)

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
