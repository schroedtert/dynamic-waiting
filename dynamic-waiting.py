import random

from lib import run_simulation


def main():
    random.seed(124)
    # random.seed(12312)
    file = open('geometries/simplified.xml', 'r')
    # plot_geometry(geometry)
    run_simulation(file)


if __name__ == '__main__':
    main()
