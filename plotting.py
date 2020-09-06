from pedestrian import Pedestrian
from geometry import Geometry
from grid import Grid
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List
import pandas as pd
import skgeom as sg
from skgeom.draw import draw
from trajectory import Trajectory
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy import ndimage
import numpy as np

from constants import MTOMM
from descartes.patch import PolygonPatch
from matplotlib.ticker import FuncFormatter


def plot_geometry_peds(geometry: Geometry, grid: Grid, peds: Dict[int, Pedestrian], highlight=None, filename=None):
    fig, ax = plt.subplots(dpi=300)

    patch = PolygonPatch(geometry.floor, facecolor='gray', edgecolor='black',
                         alpha=0.5, zorder=2)
    ax.add_patch(patch)
    for entrance in geometry.entrances.values():
        ex, ey = entrance.xy
        ax.plot(ex, ey, color='red')
    for exit in geometry.exits.values():
        ex, ey = exit.xy
        ax.plot(ex, ey, color='green')

    ax.set_ylim([-5000, 8000])
    ax.set_xlim([-56000, 10000])

    ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x / 1000), ',')))
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda y, p: format(int(y / 1000), ',')))
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_aspect(1.)
    plt.gca().set_adjustable("box")

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='png', bbox_inches='tight')


def plot_prob_field(geometry: Geometry, grid: Grid, prob_field, title="", ped=None, vmin=None, vmax=None,
                    filename=None):
    plt.figure(dpi=300)
    if not ped is None:
        x = grid.gridX[ped.i()][ped.j()]
        y = grid.gridY[ped.i()][ped.j()]

    pc = plt.pcolor(grid.gridX / MTOMM, grid.gridY / MTOMM, prob_field, cmap=cm.jet, vmin=0, vmax=2)

    plt.axis('equal')
    plt.xlabel('x/m')
    plt.ylabel('y/m')
    plt.gca().set_adjustable("box")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, dpi=300, format='png', bbox_inches='tight')
