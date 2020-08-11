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

def setup_simulation(agents):
    num_repetitions = 1
    max_agents = np.asarray([agents])
    init_agents = np.asarray([0., 0.5])
    standing_agents = np.asarray([0., 0.25, 0.5, 0.75, 1])
    steps = np.asarray([500])
    seeds = np.asarray([124, 4356, 234])
    w_exits = np.arange(1, 2.1, 1)
    w_walls = np.arange(1, 2.1, 1)
    w_attractions = np.arange(1, 2.1, 1)

    all = [max_agents, init_agents, standing_agents,
           steps, seeds, w_exits, w_walls, w_attractions]

    # file = 'geometries/simplified.xml'
    file = 'geometries/platform-smaller.xml'

    parameters = []

    for combination in itertools.product(*all):
        for rep in range(num_repetitions):
            max_agent = combination[0]
            init_agent = int(max_agent * combination[1])
            standing_agent = int(init_agent * combination[2])
            step = combination[3]
            seed = combination[4]
            w_exit = combination[5]
            w_wall = combination[6]
            w_attraction = combination[7]
            suffix = "max-agents={}_init-agents={}_standing-agents={}_steps={}_seed={}" \
                     "_w-exit={:0.2f}_w-wall={:0.2f}_w-attraction={:0.2f}_rep={}".format(
                max_agent, init_agent, standing_agent, step, seed, w_exit, w_wall, w_attraction, rep)
            output_path = os.path.join('/p/project/jias72/tobias/2020-femtc/2020-08-11_results/', suffix)

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

            if not para in parameters:
                parameters.append(para)

    return parameters


def Repeat(x):
    _size = len(x)
    repeated = []
    for i in range(_size):
        k = i + 1
        for j in range(k, _size):
            if x[i] == x[j] and x[i] not in repeated:
                repeated.append(x[i])
    return repeated

def start_simulation(sim_parameters):
    run_simulation(sim_parameters)
    return 0


if __name__ == '__main__':
    num_agents = int(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])

    parameters = setup_simulation(num_agents)

    print('run {} simulations with {} processes'.format(end-start, multiprocessing.cpu_count()))
    start_time = time.time()

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map_async(start_simulation, parameters[int(start):int(end)])
    pool.close()
    pool.join()
    end_time = time.time()

    print("Time needed: {}".format(end_time - start_time))
    print('All simulations finished')
