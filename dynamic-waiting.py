import argparse

from lib import run_simulation
from simulation_parameters import SimulationParameters


def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))
    return x


def restricted_int(x):
    try:
        x = int(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a integer literal" % (x,))
    return x


def setup_argument_parser():
    parser = argparse.ArgumentParser(description='Dynamic CA waiting model for pedestrians')

    # read general parameters
    parser.add_argument('--max_agents', help='max number of pedestrians', type=restricted_int, default=1)
    parser.add_argument('--steps', help='number of simulation steps', type=restricted_int, default=5)
    parser.add_argument('--file', help='geometry used for simulation', default='./geometries/simplified.xml')

    parser.add_argument('--seed', help='used random seed (default 124)', type=restricted_int, default=124)

    # read weights from arguments
    parser.add_argument('--w_door', help='weight of door potential (default 1)', type=restricted_float, default=1)
    parser.add_argument('--w_exit', help='weight of exit potential (default 1)', type=restricted_float, default=1)
    parser.add_argument('--w_wall', help='weight of wall potential (default 1)', type=restricted_float, default=1)
    parser.add_argument('--w_att_ground', help='weight of ground attraction potential (default 1)',
                        type=restricted_float, default=1)
    parser.add_argument('--w_att_mounted', help='weight of mounted attraction potential (default 1)',
                        type=restricted_float, default=1)

    # read sigmoid parameters
    parser.add_argument('--door_b', help='sigmoid parameter for door b (default 1)', type=restricted_float, default=1)
    parser.add_argument('--door_c', help='sigmoid parameter for door c (default 1)', type=restricted_float, default=1)

    parser.add_argument('--exit_b', help='sigmoid parameter for exit b (default 1)', type=restricted_float, default=1)
    parser.add_argument('--exit_c', help='sigmoid parameter for exit c (default 1)', type=restricted_float, default=1)

    parser.add_argument('--wall_b', help='sigmoid parameter for wall b (default 1)', type=restricted_float, default=1)
    parser.add_argument('--wall_c', help='sigmoid parameter for wall c (default 1)', type=restricted_float, default=1)

    parser.add_argument('--att_ground_b', help='sigmoid parameter for ground attraction b (default 1)',
                        type=restricted_float, default=1)
    parser.add_argument('--att_ground_c', help='sigmoid parameter for ground attraction c (default 1)',
                        type=restricted_float, default=1)

    parser.add_argument('--att_mounted_b', help='sigmoid parameter for mounted attraction b (default 1)',
                        type=restricted_float, default=1)
    parser.add_argument('--att_mounted_c', help='sigmoid parameter for mounted attraction c (default 1)',
                        type=restricted_float, default=1)

    parser.add_argument('--ped_b', help='sigmoid parameter for pedestrian b (default 1)', type=restricted_float,
                        default=1)
    parser.add_argument('--ped_c', help='sigmoid parameter for pedestrian c (default 1)', type=restricted_float,
                        default=1)

    return parser


if __name__ == '__main__':
    arg_parser = setup_argument_parser()
    simulation_parameters = SimulationParameters(arg_parser.parse_args())
    run_simulation(simulation_parameters)
