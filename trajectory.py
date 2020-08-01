from dataclasses import dataclass
from typing import Dict
import pandas as pd
from pedestrian import Pedestrian
from grid import Grid

import numpy as np

@dataclass
class Trajectory:
    traj = pd.DataFrame(columns=['step', 'id', 'x', 'y'])
    space_usage = None

    def __init__(self, grid: Grid):
        self.space_usage = np.zeros_like(grid.gridX)

    def add_step(self, step: int, grid: Grid, peds: Dict[int, Pedestrian]):
        for key, ped in peds.items():
            # add trajectory
            x, y = grid.get_coordinates(ped.pos[0], ped.pos[1])
            step_frame = {'step': step, 'id': key, 'x': x, 'y': y}
            self.traj = self.traj.append(step_frame, ignore_index=True)

            # update space usage
            self.space_usage[ped.pos[0]][ped.pos[1]] = self.space_usage[ped.pos[0]][ped.pos[1]] + 1
