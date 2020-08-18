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
    max_agents = np.asarray([100])
    init_agents = np.asarray([0.25])
    standing_agents = np.asarray([0.])
    steps = np.asarray([540])
    seeds = np.asarray([43123])
    w_exits = np.asarray([1])
    w_walls = np.asarray([1])
    w_doors = np.asarray([1])
    w_directions = np.asarray([False])

    exit_prob_0 = np.asarray([0.5])
    all = [max_agents, init_agents, standing_agents,
           steps, seeds, w_exits, w_walls, w_doors, w_directions, exit_prob_0]

    # file = 'geometries/simplified.xml'
    # file = 'geometries/platform-smaller.xml'
    # file = 'geometries/platform-sbb.xml'
    file = 'geometries/Bern_geo.xml'

    parameters = []
    suffixes = []

    for combination in itertools.product(*all):
        for rep in range(num_repetitions):
            max_agent = combination[0]
            init_agent = int(max_agent * combination[1])
            standing_agent = int(init_agent * combination[2])
            step = combination[3]
            seed = combination[4]
            w_exit = combination[5]
            w_wall = combination[6]
            w_door = combination[7]
            w_direction = combination[8]
            exit_prob = (combination[9], 1 - combination[9])

            suffix = "max-agents={:04d}_init-agents={:04d}_standing-agents={:04d}_steps={:04d}_seed={:08d}" \
                     "_w-exit={:0.2f}_w-wall={:0.2f}_w-door={:0.2f}_w-directions={:1d}_exit-prob={:0.2f}-{:0.2f}".format(
                max_agent, init_agent, standing_agent, step, seed, w_exit, w_wall, w_door, int(w_direction),
                exit_prob[0],
                exit_prob[1])

            if not suffix in suffixes:
                suffixes.append(suffix)
                print(suffix)
            else:
                continue

            # output_path = os.path.join('results-change-weight', suffix)
            # output_path = os.path.join('/p/project/jias72/tobias/2020-femtc/2020-08-15_sbb', suffix)
            # output_path = os.path.join('/p/project/jias72/tobias/2020-femtc/2020-08-16_real-bern', suffix)
            output_path = os.path.join('results-ff', suffix)

            para = SimulationParameters()
            para.max_agents = max_agent
            para.init_agents = init_agent
            para.standing_agents = standing_agent
            para.steps = step
            para.seed = seed
            para.w_door = 1
            para.w_exit = w_exit
            para.w_wall = w_wall
            para.w_door = w_door
            para.output_path = output_path
            para.exit_prob = exit_prob
            para.plot = False
            para.file = file
            para.w_direction = w_direction
            parameters.append(para)

    return parameters


def start_simulation(sim_parameters):
    # run_simulation(sim_parameters)
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
