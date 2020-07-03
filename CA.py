from geometry import Geometry
from geometry import Geometry
from grid import Grid


class CA:
    staticFF = None

    def __init__(self, geometry: Geometry, grid: Grid):
        self.staticFF = compute_static_ff(geometry, grid)

    def compute_step(self, geometry: Geometry, grid: Grid):
        return
