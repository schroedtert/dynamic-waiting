from dataclasses import dataclass


@dataclass
class Pedestrian:
    '''Class containing ped information'''
    pos: [int, int]

    def i(self):
        return self.pos[0]

    def j(self):
        return self.pos[1]
