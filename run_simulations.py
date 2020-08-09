import itertools

import numpy as np
import os
import subprocess
import sys
import multiprocessing

from simulation_parameters import *
from lib import run_simulation

import time


# with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
#     waiting_ca.main()

def setup_simulation():
    num_repetitions = 2
    max_agents = np.arange(50, 301, 50)
    init_agents = np.arange(0, 101, 50)
    standing_agents = np.arange(0, 101, 50)
    steps = np.asarray([150])
    seeds = np.asarray([124, 4356, 234])
    w_exits = np.arange(1, 2.1, 0.5)
    w_walls = np.arange(1, 2.1, 0.5)
    w_attractions = np.arange(1, 2.1, 0.5)

    all = [max_agents, init_agents, standing_agents,
           steps, seeds, w_exits, w_walls, w_attractions]

    # file = 'geometries/simplified.xml'
    file = 'geometries/platform.xml'

    parameters = []

    for combination in itertools.product(*all):
        for rep in range(num_repetitions):
            max_agent = combination[0]
            init_agent = combination[1]
            standing_agent = combination[2]
            step = combination[3]
            seed = combination[4]
            w_exit = combination[5]
            w_wall = combination[6]
            w_attraction = combination[7]
            suffix = "max-agents={}_init-agents={}_standing-agents={}_steps={}_seed={}" \
                     "_w-exit={:0.2f}_w-wall={:0.2f}_w-attraction={:0.2f}_rep={}".format(
                max_agent, init_agent, standing_agent, step, seed, w_exit, w_wall, w_attraction, rep)
            output_path = os.path.join('results/', suffix)

            para = SimulationParameters()
            para.max_agents = max_agent
            para.init_agents = init_agent
            para.standing_agents = standing_agent
            para.steps = step
            para.seed = seed
            para.w_door = 0
            para.w_exit = w_exit
            para.w_wall = w_wall
            para.w_attraction = w_attraction
            para.output_path = output_path
            para.plot = False
            para.file = file

            parameters.append(para)

    return parameters


def start_simulation(sim_parameters):
    run_simulation(sim_parameters)


if __name__ == '__main__':
    start = int(sys.argv[1])
    end = int(sys.argv[2])

    parameters = setup_simulation()
    print('run {} simulations with {} processes'.format(len(parameters), multiprocessing.cpu_count()))
    print(parameters[int(start):int(end)])
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    start = time.time()
    pool.map(start_simulation, parameters[int(start):int(end)])
    pool.close()
    pool.join()
    end = time.time()
    print("Time needed: {}".format(end - start))

    print('All simulations finished')
