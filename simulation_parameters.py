from dataclasses import dataclass


@dataclass
class SimulationParameters:
    # general parameters
    max_agents: int
    init_agents: int
    steps: int
    seed: int
    file = ''

    # for wall distance
    wall_b: float = 1
    wall_c: float = 1

    # for ped distance
    ped_b: float = 5
    ped_c: float = 1

    # for door distance (flow avoidance)
    door_b: float = 10
    door_c: float = 0.5

    # for exit distance
    exit_b: float = 5
    exit_c: float = 0.5

    # for attraction prob ground
    attraction_ground_b: float = 2
    attraction_ground_c: float = 0.5

    attraction_mounted_b: float = 2
    attraction_mounted_c: float = 0.1

    # weights
    w_door: float = 1
    w_exit: float = 1
    w_attraction_ground: float = 1
    w_attraction_mounted: float = 1
    w_wall: float = 1

    def __init__(self, args):
        self.max_agents = args.max_agents
        self.init_agents = args.init_agents
        self.steps = args.steps
        self.seed = args.seed
        self.file = args.file

        self.w_door = args.w_door
        self.w_exit = args.w_exit
        self.w_wall = args.w_wall
        self.w_attraction_ground = args.w_att_ground
        self.w_attraction_mounted = args.w_att_mounted

        self.door_b = args.door_b
        self.door_c = args.door_c

        self.exit_b = args.exit_b
        self.exit_c = args.exit_c

        self.wall_b = args.wall_b
        self.wall_c = args.wall_b

        self.attraction_ground_b = args.att_ground_b
        self.attraction_ground_c = args.att_ground_c

        self.attraction_mounted_b = args.att_mounted_b
        self.attraction_mounted_c = args.att_mounted_c

        self.ped_b = args.ped_b
        self.ped_c = args.ped_c
