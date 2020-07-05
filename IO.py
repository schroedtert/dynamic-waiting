import numpy as np

# parsing xml files
from xml.dom.minidom import parse
from typing import Final

MTOMM: Final = 1000

def read_geometry(filename):
    root = parse(filename)
    obstacles = read_obstacle(root)
    walls = read_subroom_walls(root)
    doors = read_doors(root)
    edges = read_subroom_edges(root)
    return walls, obstacles, doors, edges


def read_doors(root):
    # Initialization of a dictionary with obstacles
    doors = {}

    # read in obstacles and combine them into an array for polygon representation
    for t_num, t_elem in enumerate(root.getElementsByTagName('transition')):
        id = t_elem.getAttribute('id')

        points = []
        for v_num, v_elem in enumerate(t_elem.getElementsByTagName('vertex')):
            vertex_x = MTOMM * float(t_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
            vertex_y = MTOMM * float(t_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
            points.append([vertex_x, vertex_y])

        doors[id] = points

    return doors


def read_obstacle(xml_doc):
    # Initialization of a dictionary with obstacles
    obstacles = {}
    # read in obstacles and combine them into an array for polygon representation
    for o_num, o_elem in enumerate(xml_doc.getElementsByTagName('obstacle')):
        id = o_elem.getAttribute('id')

        points = []
        for p_num, p_elem in enumerate(o_elem.getElementsByTagName('polygon')):
            for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                vertex_x = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
                vertex_y = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
                points.append([vertex_x, vertex_y])

        obstacles[id] = points

    return obstacles


def read_subroom_edges(xml_doc):
    n_wall = 0
    edge_segments = []
    for s_num, s_elem in enumerate(xml_doc.getElementsByTagName('subroom')):
        for p_num, p_elem in enumerate(s_elem.getElementsByTagName('edge')):
            n_wall = n_wall + 1
            n_vertex = len(p_elem.getElementsByTagName('vertex'))

            edge_points = []
            for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                x = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value)
                y = MTOMM * float(p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value)
                edge_points.append([x, y])

            edge_segments.append([edge_points[0], edge_points[1]])

    return edge_segments


def read_subroom_walls(xml_doc):
    n_wall = 0
    wall_points = []
    for s_num, s_elem in enumerate(xml_doc.getElementsByTagName('subroom')):
        for p_num, p_elem in enumerate(s_elem.getElementsByTagName('polygon')):
            if p_elem.getAttribute('caption') == "wall":
                n_wall = n_wall + 1
                n_vertex = len(p_elem.getElementsByTagName('vertex'))

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


def geo_limits(geo_xml):
    geometry_wall = read_subroom_walls(geo_xml)
    geominX = MTOMM * 1000
    geomaxX = MTOMM * -1000
    geominY = MTOMM * 1000
    geomaxY = MTOMM * -1000
    Xmin = []
    Ymin = []
    Xmax = []
    Ymax = []
    for k in geometry_wall.keys():
        Xmin.append(np.min(geometry_wall[k][:, 0]))
        Ymin.append(np.min(geometry_wall[k][:, 1]))
        Xmax.append(np.max(geometry_wall[k][:, 0]))
        Ymax.append(np.max(geometry_wall[k][:, 1]))

    geominX = np.min(Xmin)
    geomaxX = np.max(Xmax)
    geominY = np.min(Ymin)
    geomaxY = np.max(Ymax)
    return geominX, geomaxX, geominY, geomaxY
