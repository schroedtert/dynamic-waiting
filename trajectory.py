from dataclasses import dataclass
from typing import Dict
import pandas as pd
from pedestrian import Pedestrian
from grid import Grid


@dataclass
class Trajectory:
    traj = pd.DataFrame(columns=['step', 'id', 'x', 'y'])

    def add_step(self, step: int, grid: Grid, peds: Dict[int, Pedestrian]):
        for key, ped in peds.items():
            x, y = grid.get_coordinates(ped.pos[0], ped.pos[1])
            step_frame = {'step': step, 'id': key, 'x': x, 'y': y}
            self.traj = self.traj.append(step_frame, ignore_index=True)
