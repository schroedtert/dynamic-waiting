import numpy as np
import pandas as pd

# parsing xml files
from xml.dom.minidom import parse
from typing import Dict

from pedestrian import Pedestrian
from geometry import Geometry, Grid

from shapely.geometry import asPolygon, Polygon, LineString
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def read_geometry(filename) -> Geometry:
    root = parse(filename)
    obstacles = read_obstacle(root)
    subroom = read_subroom_walls(root)
    doors = read_doors(root)
    return Geometry(subroom, obstacles, doors, {})

def read_doors(root):
    # Initialization of a dictionary with obstacles
    doors = {}
    # read in obstacles and combine them into an array for polygon representation
    for t_num, t_elem in enumerate(root.getElementsByTagName('transition')):
        id = t_elem.getAttribute('id')

        points = []
        for v_num, v_elem in enumerate(t_elem.getElementsByTagName('vertex')):
            vertex_x = float(t_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
            vertex_y = float(t_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
            points.append(np.vstack([vertex_x, vertex_y]))

        doors[id] = LineString(points)

    return doors

def read_obstacle(xml_doc):
    # Initialization of a dictionary with obstacles
    obstacles = {}
    # read in obstacles and combine them into an array for polygon representation
    for o_num, o_elem in enumerate(xml_doc.getElementsByTagName('obstacle')):
        id = o_elem.getAttribute('id')

        points = np.zeros((0, 2))
        for p_num, p_elem in enumerate(o_elem.getElementsByTagName('polygon')):
            for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                vertex_x = float(p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
                vertex_y = float(p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
                points = np.vstack([points , [vertex_x, vertex_y]])

        points = np.unique(points, axis=0)
        x = points[:, 0]
        y = points[:, 1]
        n = len(points)
        center_point = [np.sum(x)/n, np.sum(y)/n]
        angles = np.arctan2(x-center_point[0],y-center_point[1])
        ##sorting the points:
        sort_tups = sorted([(i,j,k) for i,j,k in zip(x,y,angles)], key = lambda t: t[2])
        obstacles[id] = np.array(sort_tups)[:,0:2]

    dict_polygons = {}
    for key, value in obstacles.items():
        dict_polygons[key] = asPolygon(value)

    return dict_polygons


def read_subroom_walls(xml_doc):
    dict_polynom_wall = {}
    n_wall = 0
    for s_num, s_elem in enumerate(xml_doc.getElementsByTagName('subroom')):
        for p_num, p_elem in enumerate(s_elem.getElementsByTagName('polygon')):
            if p_elem.getAttribute('caption') == "wall":
                n_wall = n_wall + 1
                n_vertex = len(p_elem.getElementsByTagName('vertex'))
                vertex_array = np.zeros((n_vertex, 2))

                for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                    vertex_array[v_num, 0] = p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value
                    vertex_array[v_num, 1] = p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value

                dict_polynom_wall[n_wall] = vertex_array

    dict_polygons = {}
    for key, value in dict_polynom_wall.items():
        dict_polygons[key] = asPolygon(value)

    return dict_polygons


def geo_limits(geo_xml):
    geometry_wall = read_subroom_walls(geo_xml)
    geominX=1000
    geomaxX=-1000
    geominY=1000
    geomaxY=-1000
    Xmin = []
    Ymin = []
    Xmax = []
    Ymax = []
    for k in geometry_wall.keys():
        Xmin.append(np.min(geometry_wall[k][:,0]))
        Ymin.append(np.min(geometry_wall[k][:,1]))
        Xmax.append(np.max(geometry_wall[k][:,0]))
        Ymax.append(np.max(geometry_wall[k][:,1]))

    geominX = np.min(Xmin)
    geomaxX = np.max(Xmax)
    geominY = np.min(Ymin)
    geomaxY = np.max(Ymax)
    return geominX, geomaxX, geominY, geomaxY

def plot_geometry(geometry:Geometry):
    plt.figure()
    for key, polygon in geometry.bounds.items():
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black')

    for key, obstacle in geometry.obstacles.items():
        x, y = obstacle.exterior.xy
        plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        plt.plot(x, y, color='gray')

    for key, door in geometry.doors.items():
        x, y = door.coords.xy
        plt.plot(x, y, color='red')

    plt.show()

def plot_geometry_grid(geometry: Geometry, grid: Grid):
    plt.figure()
    for key, polygon in geometry.bounds.items():
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black')

    for key, obstacle in geometry.obstacles.items():
        x, y = obstacle.exterior.xy
        plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        plt.plot(x, y, color='gray')

    for key, door in geometry.doors.items():
        x, y = door.coords.xy
        plt.plot(x, y, color='red')

    for i in range(grid.gridX.shape[0]):
        x = [grid.gridX[i][0], grid.gridX[i][-1]]
        y = [grid.gridY[i], grid.gridY[i]]
        plt.plot(x, y, color='gray', alpha=0.1)

    for i in range(grid.dimX):
        for j in range(grid.dimY):
            x,y = grid.getCoordinates(i, j)
            cellsize = grid.cellsize
            rect = plt.Rectangle((x-0.5*cellsize, y-0.5*cellsize), cellsize, cellsize, fill=False)
            ax = plt.gca()
            ax.add_patch(rect)

    plt.show()

def plot_geometry_peds(geometry: Geometry, grid: Grid, peds: Dict[int, Pedestrian]):
        plt.figure()
        for key, polygon in geometry.bounds.items():
            x, y = polygon.exterior.xy
            plt.plot(x, y, color='black')

        for key, obstacle in geometry.obstacles.items():
            x, y = obstacle.exterior.xy
            plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
            plt.plot(x, y, color='gray')

        for key, door in geometry.doors.items():
            x, y = door.coords.xy
            plt.plot(x, y, color='red')

        for key, ped in peds.items():
            x = grid.gridX[ped.i()][ped.j()]
            y = grid.gridY[ped.i()][ped.j()]

            plt.plot(x, y, color='blue', markersize='8', marker='o')
        plt.show()

def plot_marked_zells(geometry: Geometry, grid: Grid, marked_cells: [[int, int]]):
    plt.figure()
    for key, polygon in geometry.bounds.items():
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black')

    for key, obstacle in geometry.obstacles.items():
        x, y = obstacle.exterior.xy
        plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        plt.plot(x, y, color='gray')

    # for key, door in geometry.doors.items():
    #     x, y = door.coords.xy
    #     plt.plot(x, y, color='red')
    for cell in marked_cells:
        x,y = grid.getCoordinates(cell[0], cell[1])
        cellsize = grid.cellsize
        rect = plt.Rectangle((x-0.5*cellsize, y-0.5*cellsize), cellsize, cellsize, fill=False)
        ax = plt.gca()
        ax.add_patch(rect)

    plt.show()

def plot_prob_field(geometry: Geometry, grid: Grid, probField):
    plt.figure()
    # plt.contour(grid.gridX, grid.gridY, phi, [0], linewidths=(3), colors='black')
    for key, polygon in geometry.bounds.items():
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='black')

    for key, obstacle in geometry.obstacles.items():
        x, y = obstacle.exterior.xy
        plt.fill(x, y, alpha=0.1, fc='gray', ec='none')
        plt.plot(x, y, color='gray')

    for key, door in geometry.doors.items():
        x, y = door.coords.xy
        plt.plot(x, y, color='red')

    plt.contour(grid.gridX, grid.gridY, probField)
    plt.colorbar()
    plt.show()
