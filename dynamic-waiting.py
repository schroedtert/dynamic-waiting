import random

from lib import run_simulation


def main():
    random.seed(124)
    file = open('geometries/simplified.xml', 'r')
    # plot_geometry(geometry)
    run_simulation(file, 1)


if __name__ == '__main__':
    main()
