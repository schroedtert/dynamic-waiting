import numpy as np
import os
from xml.dom.minidom import parse
from constants import *
from CA import *


def read_geometry(filename):
    """
    Reads the geometry from filename
    :param filename: file containing geometry information
    :return: geometrical features
    """
    root = parse(filename)
    obstacles = read_obstacle(root)
    walls = read_subroom_walls(root)
    entrances, entrances_properties = read_entrances(root)
    exits = read_exits(root)
    edges = read_subroom_edges(root)
    return walls, obstacles, entrances, entrances_properties, exits, edges


def read_entrances(root):
    """
    Reads the entrances.
    :param root: xml root to start parsing
    :return: Entrances defined in xml file
    """
    # Initialization of a dictionary with obstacles
    entrances = {}
    entrances_properties = {}
    # read in doors and combine them into an array for polygon representation
    for t_num, t_elem in enumerate(root.getElementsByTagName('entrance')):
        door_id = int(t_elem.getAttribute('id'))
        door_frequency = int(t_elem.getAttribute('frequency'))
        door_number = int(t_elem.getAttribute('number'))
        entrances_properties[door_id] = (door_frequency, door_number)

        points = []
        for v_num, v_elem in enumerate(t_elem.getElementsByTagName('vertex')):
            vertex_x = MTOMM * float(t_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
            vertex_y = MTOMM * float(t_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
            points.append([vertex_x, vertex_y])

        entrances[door_id] = points

    return entrances, entrances_properties


def read_exits(root):
    """
    Reads the exits.
    :param root: xml root to start parsing
    :return: Exits defined in xml file
    """
    # Initialization of a dictionary with obstacles
    exits = {}

    # read in doors and combine them into an array for polygon representation
    for t_num, t_elem in enumerate(root.getElementsByTagName('exit')):
        door_id = int(t_elem.getAttribute('id'))

        points = []
        for v_num, v_elem in enumerate(t_elem.getElementsByTagName('vertex')):
            vertex_x = MTOMM * float(t_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
            vertex_y = MTOMM * float(t_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
            points.append([vertex_x, vertex_y])

        exits[door_id] = points

    return exits


def read_obstacle(xml_doc):
    """
    Reads the obstacles.
    :param root: xml root to start parsing
    :return: Obstacles defined in xml file
    """
    # Initialization of a dictionary with obstacles
    obstacles = {}
    # read in obstacles and combine them into an array for polygon representation
    for o_num, o_elem in enumerate(xml_doc.getElementsByTagName('obstacle')):
        obstacle_id = int(o_elem.getAttribute('id'))

        points = []
        for p_num, p_elem in enumerate(o_elem.getElementsByTagName('polygon')):
            for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                vertex_x = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
                vertex_y = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
                points.append([vertex_x, vertex_y])

        obstacles[obstacle_id] = points

    return obstacles


def read_subroom_edges(xml_doc):
    """
    Reads the edges.
    :param root: xml root to start parsing
    :return: Edges defined in xml file
    """

    n_wall = 0
    edge_segments = []
    for s_num, s_elem in enumerate(xml_doc.getElementsByTagName('subroom')):
        for p_num, p_elem in enumerate(s_elem.getElementsByTagName('edge')):
            n_wall = n_wall + 1

            edge_points = []
            for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                x = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
                y = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
                edge_points.append([x, y])

            edge_segments.append([edge_points[0], edge_points[1]])

    return edge_segments


def read_subroom_walls(xml_doc):
    """
    Reads the walls.
    :param root: xml root to start parsing
    :return: Walls defined in xml file
    """
    n_wall = 0
    wall_points = []
    for s_num, s_elem in enumerate(xml_doc.getElementsByTagName('subroom')):
        for p_num, p_elem in enumerate(s_elem.getElementsByTagName('polygon')):
            if p_elem.getAttribute('caption') == "wall":
                n_wall = n_wall + 1

                for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                    x = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
                    y = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
                    wall_points.append([x, y])

    wall_segments = []
    for i in range(len(wall_points)):
        point1 = wall_points[i]
        point2 = wall_points[(i + 1) % len(wall_points)]
        wall_segments.append([point1, point2])

    return wall_segments


def create_output_directory(output_path):
    """
    Creates the output directory
    :param output_path: path to the output directory
    """
    try:
        # Create target Directory
        os.makedirs(output_path)
        print('Created {}'.format(output_path))
    except FileExistsError:
        print('{} already exists, results will be overwritten'.format(output_path))
        return


def save_floor_field(floor_field, output_path, filename):
    """
    Save the floor field to a file.
    :param floor_field: floor field to save
    :param output_path: path to output directory
    :param filename: filename to save the ff
    """
    ff_filename = os.path.join(output_path, filename)
    np.savetxt(ff_filename, floor_field)
