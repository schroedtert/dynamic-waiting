from dataclasses import dataclass
from typing import Dict
import pandas as pd
from pedestrian import Pedestrian
from grid import Grid

import numpy as np
import os


@dataclass
class Trajectory:
    """
    Class containing the trajectory data
    """
    traj = pd.DataFrame(columns=['step', 'id', 'x', 'y', 'exit'])
    space_usage = None

    def __init__(self, grid: Grid, num_steps: int):
        """
        Constructor
        :param grid: grid to use
        :param num_steps: number of compute steps
        """
        shape = (num_steps, grid.gridX.shape[0], grid.gridX.shape[1])
        self.space_usage = np.zeros(shape)

    def add_step(self, step: int, grid: Grid, peds: Dict[int, Pedestrian], output_path):
        """
        Append trajectory data.
        :param step: Current time step
        :param grid: Grid to use
        :param peds: Pedestrians in simulation
        :param output_path: output_path
        """
        step_frame = pd.DataFrame(columns=['step', 'id', 'x', 'y', 'exit'])
        for key, ped in peds.items():
            # add trajectory
            x, y = grid.get_coordinates(ped.pos[0], ped.pos[1])
            step_frame_ped = {'step': step, 'id': key, 'x': x, 'y': y, 'exit': ped.exit_id}
            step_frame = step_frame.append(step_frame_ped, ignore_index=True)

            # update space usage
            if step != 0:
                self.space_usage[step][ped.pos[0]][ped.pos[1]] = self.space_usage[step - 1][ped.pos[0]][ped.pos[1]] + 1
            else:
                self.space_usage[step][ped.pos[0]][ped.pos[1]] = self.space_usage[0][ped.pos[0]][ped.pos[1]] + 1

        traj_filename = os.path.join(output_path, 'traj.csv')

        if step == 0:
            with open(traj_filename, 'w') as f:
                step_frame.to_csv(f, header=True, index=False)
        else:
            with open(traj_filename, 'a') as f:
                step_frame.to_csv(f, header=False, index=False)

        self.traj = self.traj.append(step_frame, ignore_index=True)

    def save(self, output_path):
        """
        Saves the current state of the trajectory
        :param output_path: output directory
        """
        traj_filename = os.path.join(output_path, 'traj.csv')
        self.traj.to_csv(traj_filename)

        step = self.space_usage.shape[0] - 1

        suffix = 'space_usage.txt'
        su_filename = os.path.join(output_path, suffix)
        np.savetxt(su_filename, self.space_usage[step])
