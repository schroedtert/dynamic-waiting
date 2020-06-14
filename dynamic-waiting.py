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
    random.seed(5)
    file = open('geometries/simplified.xml', 'r')
    # plot_geometry(geometry)
    run_simulation(file, 20)

if __name__ == '__main__':
    main()