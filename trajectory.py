from dataclasses import dataclass
from typing import Dict
import pandas as pd
from pedestrian import Pedestrian
from grid import Grid

import numpy as np
import os

@dataclass
class Trajectory:
    traj = pd.DataFrame(columns=['step', 'id', 'x', 'y'])
    space_usage = None

    def __init__(self, grid: Grid, num_steps: int):
        shape = (num_steps, grid.gridX.shape[0], grid.gridX.shape[1])
        self.space_usage = np.zeros(shape)

    def add_step(self, step: int, grid: Grid, peds: Dict[int, Pedestrian]):
        for key, ped in peds.items():
            # add trajectory
            x, y = grid.get_coordinates(ped.pos[0], ped.pos[1])
            step_frame = {'step': step, 'id': key, 'x': x, 'y': y}
            self.traj = self.traj.append(step_frame, ignore_index=True)

            # update space usage
            if step != 0:
                self.space_usage[step][ped.pos[0]][ped.pos[1]] = self.space_usage[step - 1][ped.pos[0]][ped.pos[1]] + 1
            else:
                self.space_usage[step][ped.pos[0]][ped.pos[1]] = self.space_usage[0][ped.pos[0]][ped.pos[1]] + 1

    def save(self, output_path):
        traj_filename = os.path.join(output_path, 'traj.csv')
        self.traj.to_csv(traj_filename)

        for step in range(self.space_usage.shape[0]):
            suffix = 'space_usage_{:03d}.txt'.format(step)
            su_filename = os.path.join(output_path, suffix)
            np.savetxt(su_filename, self.space_usage[step])
