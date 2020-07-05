from geometry import Geometry
from geometry import Geometry
from grid import Grid


class CA:
    staticFF = None

    def __init__(self, geometry: Geometry, grid: Grid):
        self.staticFF = compute_static_ff(geometry, grid)

    def compute_step(self, geometry: Geometry, grid: Grid):
        dynamicFF = compute_dynamic_ff(geometry, grid)
        filterFF = compute_filter_ff(geometry, grid)
        combined = compute_overall_ff(geometry, grid, self.staticFF, dynamicFF, filterFF)

        for key, ped in geometry.peds.items():
            computeFFforPed(geometry, grid, ped, combined)

        return
