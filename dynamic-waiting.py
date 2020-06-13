import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time
import logging
import argparse
import os
import random

from lib import run_simulation

def main():
    random.seed(1)
    file = open('geometries/simplified.xml', 'r')
    # plot_geometry(geometry)
    run_simulation(file, 1)

if __name__ == '__main__':
    main()