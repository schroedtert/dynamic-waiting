from dataclasses import dataclass
from constants import *


@dataclass
class Pedestrian:
    """Class containing ped information"""
    pos: [int, int]
    direction: Neighbors
    id: int
    standing: bool
    exit_id: int
    not_moving: int = 1

    def i(self):
        return self.pos[0]

    def j(self):
        return self.pos[1]

    def set_pos(self, new_pos):
        if new_pos[0] < self.pos[0] and new_pos[1] == self.pos[1]:
            self.direction = Neighbors.left
            self.not_moving = 1
        elif new_pos[0] > self.pos[0] and new_pos[1] == self.pos[1]:
            self.direction = Neighbors.right
            self.not_moving = 1
        elif new_pos[0] == self.pos[0] and new_pos[1] < self.pos[1]:
            self.direction = Neighbors.bottom
            self.not_moving = 1
        elif new_pos[0] == self.pos[0] and new_pos[1] > self.pos[1]:
            self.direction = Neighbors.top
            self.not_moving = 1
        elif new_pos[0] == self.pos[0] and new_pos[1] == self.pos[1]:
            self.direction = Neighbors.self
            self.not_moving = self.not_moving + 1
        else:
            print('something wrong')
        self.pos = new_pos
