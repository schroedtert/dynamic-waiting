from dataclasses import dataclass


@dataclass
class Pedestrian:
    '''Class containing ped information'''
    pos: [int, int]

    def i(self):
        return self.pos[0]

    def j(self):
        return self.pos[1]

    def set_pos(self, new_pos):
        self.pos = new_pos
