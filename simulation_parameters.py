from dataclasses import dataclass
import pandas as pd
import os


@dataclass
class SimulationParameters:
    # general parameters
    max_agents: int
    init_agents: int
    standing_agents: int
    steps: int
    seed: int
    file = ''

    # for wall distance
    wall_b: float = 1.5
    wall_c: float = 1

    # for ped distance
    ped_b: float = 1
    ped_c: float = 1

    # for door distance (flow avoidance)
    door_b: float = 1
    door_c: float = 0.5

    # for exit distance
    exit_b: float = 3.0
    exit_c: float = 0.25

    # for attraction prob ground
    attraction_ground_b: float = 2
    attraction_ground_c: float = 0.5

    attraction_mounted_b: float = 2
    attraction_mounted_c: float = 0.1

    # weights
    w_door: float = 1
    w_exit: float = 1
    w_attraction: float = 1
    w_wall: float = 1

    w_direction: bool = False

    plot: bool = False

    exit_prob = [0.5, 0.5]
    output_path = 'results'

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            self.init_from_parser(args[0])

    def init_from_para(self, max_agents, init_agents, standing_agents, steps, seed,
                       w_door, w_exit, w_wall, w_attraction, output_path, plot, file):
        self.max_agents = max_agents
        self.init_agents = init_agents
        self.standing_agents = standing_agents
        self.steps = steps
        self.seed = seed
        self.w_door = w_door
        self.w_exit = w_exit
        self.w_wall = w_wall
        self.w_attraction = w_attraction
        self.output_path = output_path
        self.plot = False
        self.file = file

    def init_from_parser(self, args):
        self.max_agents = args.max_agents
        self.init_agents = args.init_agents
        self.standing_agents = args.standing_agents
        self.steps = args.steps
        self.seed = args.seed
        self.file = args.file

        self.w_exit = args.w_exit
        self.w_wall = args.w_wall

        self.door_b = args.door_b
        self.door_c = args.door_c

        self.exit_b = args.exit_b
        self.exit_c = args.exit_c

        self.wall_b = args.wall_b
        self.wall_c = args.wall_b

        self.ped_b = args.ped_b
        self.ped_c = args.ped_c

        self.plot = args.plot
        self.output_path = args.output_path

    def write_to_file(self, output_path):
        df = pd.DataFrame({'seed': [self.seed],
                           'steps': [self.steps],
                           'max_agents': [self.max_agents],
                           'init_agents': [self.init_agents],
                           'standing_agents': [self.standing_agents],
                           'exit_prob': [self.exit_prob],
                           'w_exit': [self.w_exit],
                           'w_wall': [self.w_wall],
                           'w_attraction': [self.w_attraction],
                           'exit_b': [self.exit_b],
                           'exit_c': [self.exit_c],
                           'wall_b': [self.wall_b],
                           'wall_c': [self.wall_c],
                           'att_ground_b': [self.attraction_ground_b],
                           'att_ground_c': [self.attraction_ground_c],
                           'att_mounted_b': [self.attraction_mounted_b],
                           'att_mounted_c': [self.attraction_mounted_c],
                           'ped_b': [self.ped_b],
                           'ped_c': [self.ped_c],
                           'file': [self.file]})

        filename = os.path.join(output_path, 'simulation_parameters.csv')
        df.to_csv(filename)
