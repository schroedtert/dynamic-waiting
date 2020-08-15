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
    init_agents = np.asarray([0.1])
    standing_agents = np.asarray([0.])
    steps = np.asarray([300])
    seeds = np.asarray([1224, 4356, 234, 4561, 8147, 56351])
    w_exits = np.arange(1, 2.1, 7)
    w_walls = np.arange(1.5, 2.7, 2)
    w_attractions = np.arange(1, 2.1, 2)

    all = [max_agents, init_agents, standing_agents,
           steps, seeds, w_exits, w_walls, w_attractions]

    # file = 'geometries/simplified.xml'
    # file = 'geometries/platform-smaller.xml'
    file = 'geometries/platform-sbb.xml'

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
            suffix = "max-agents={:04d}_init-agents={:04d}_standing-agents={:04d}_steps={:04d}_seed={:08d}" \
                     "_w-exit={:0.2f}_w-wall={:0.2f}_w-attraction={:0.2f}_rep={:02d}".format(
                max_agent, init_agent, standing_agent, step, seed, w_exit, w_wall, w_attraction, rep)
            # output_path = os.path.join('results-change-weight', suffix)
            output_path = os.path.join('results/sbb-train-stations-7', suffix)

            para = SimulationParameters()
            para.max_agents = max_agent
            para.init_agents = init_agent
            para.standing_agents = standing_agent
            para.steps = step
            para.seed = seed
            para.w_door = 1
            para.w_exit = w_exit
            para.w_wall = w_wall
            para.w_attraction = w_attraction
            para.output_path = output_path
            para.plot = False
            para.file = file

            if not para in parameters:
                parameters.append(para)

    return parameters


def start_simulation(sim_parameters):
    try:
        return (None, run_simulation(sim_parameters))
    except Exception as e:
        print(e)
        return (e, None)


if __name__ == '__main__':
    num_agents = int(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])

    parameters = setup_simulation(num_agents)
    print('run {} simulations with {} processes'.format(end - start, multiprocessing.cpu_count()))
    start_time = time.time()

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map_async(start_simulation, parameters[int(start):int(end)])
    pool.close()
    pool.join()
    # start_simulation(parameters[0])
    end_time = time.time()

    print("Time needed: {}".format(end_time - start_time))
    print('All simulations finished')
