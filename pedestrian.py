from dataclasses import dataclass
from constants import *


@dataclass
class Pedestrian:
    """Class containing ped information"""
    pos: [int, int]
    direction: Neighbors
    id: int

    def i(self):
        return self.pos[0]

    def j(self):
        return self.pos[1]

    def set_pos(self, new_pos):
        if new_pos[0] < self.pos[0] and new_pos[1] == self.pos[1]:
            self.direction = Neighbors.left
        elif new_pos[0] > self.pos[0] and new_pos[1] == self.pos[1]:
            self.direction = Neighbors.right
        elif new_pos[0] == self.pos[0] and new_pos[1] < self.pos[1]:
            self.direction = Neighbors.bottom
        elif new_pos[0] == self.pos[0] and new_pos[1] > self.pos[1]:
            self.direction = Neighbors.top
        elif new_pos[0] == self.pos[0] and new_pos[1] == self.pos[1]:
            self.direction = Neighbors.self
        else:
            print('something wrong')
        self.pos = new_pos
