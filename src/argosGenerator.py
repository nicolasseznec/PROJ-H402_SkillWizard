import math
from xml.dom import minidom
import xml.etree.ElementTree as ET

from src.mission import Mission, Arena
from src.util import Shape


def addTitle(element, title):
    titleStr = ' * ' + title + ' * '
    line = ' ' + '*' * (len(titleStr) - 2) + ' '

    element.append(ET.Comment(line))
    element.append(ET.Comment(titleStr))
    element.append(ET.Comment(line))


def addBox(parent, id, size=(1, 1, 1), position=(0, 0, 0), orientation=(0, 0, 0), movable=False):
    size_str = "{},{},{}".format(*size)
    position_str = "{},{},{}".format(*position)
    orientation_str = "{},{},{}".format(*orientation)

    box = ET.SubElement(parent, "box", id=id, size=size_str, movable=str(movable).lower())
    ET.SubElement(box, "body", position=position_str, orientation=orientation_str)


def addWall(parent, index, length, angle, x, y):
    addBox(parent, "wall_" + str(index), size=(0.01, length, 0.08), position=(x, y, 0), orientation=(angle, 0, 0))


def generateArenaBorders(arena: Arena, element):
    shape = Shape[arena.shape]

    if shape == Shape.Square:
        pass
    elif shape == Shape.Circle:
        pass
    else:
        if shape == Shape.Hexagon:
            n = 6
        elif shape == Shape.Octagon:
            n = 8
        elif shape == Shape.Dodecagon:
            n = 12
        else:
            n = 3

        angle = 360 / n

        radius = arena.sideLength / (2 * math.tan(math.radians(angle/2)))

        offset = angle / 2 if shape == Shape.Hexagon else 0

        for i in range(n):
            x = radius * math.cos(math.radians(angle * i + offset))
            y = radius * math.sin(math.radians(angle * i + offset))
            addWall(element, i+1, arena.sideLength, angle * i + offset, round(x, 3), round(y, 3))


def generateArena(arena: Arena, element):
    arenaElement = ET.SubElement(element, "arena", size="10, 10, 1", center="0,0,0")

    arenaElement.append(ET.Comment("{} arena with side of length {}".format(arena.shape, arena.sideLength)))
    generateArenaBorders(arena, arenaElement)
    arenaElement.tail = " "


def generateArgosFile(mission: Mission, file_name, **options):
    root = ET.Element("argos-configuration")

    if "source" in options:
        disclaimer = ET.Comment("Generated from " + str(options["source"]))
        disclaimer.tail = " "
        root.append(disclaimer)

    # Framework
    addTitle(root, "Framework")
    framework = ET.SubElement(root, "framework")
    ET.SubElement(framework, "experiment", length="60", ticks_per_second="10", random_seed="0")
    framework.tail = " "

    # Loop functions
    addTitle(root, "Loop functions")
    loop_functions = ET.SubElement(root, "loop_functions")  # TODO : library, lable
    # ET.SubElement(loop_functions, "params", )
    loop_functions.tail = " "

    # Controllers
    addTitle(root, "Controllers")
    controllers = ET.SubElement(root, "controllers")  # TODO : controllers
    controllers.tail = " "

    # Arena
    addTitle(root, "Arena")
    generateArena(mission.arena, root)

    # all floors
    # all lights
    # all walls
    # all obstacles

    # E-Puck
    # distribute

    # Physics engines
    addTitle(root, "Physics engines")
    physics_engines = ET.SubElement(root, "physics_engines")
    ET.SubElement(physics_engines, "dynamics2d", id="dyn2d")
    physics_engines.tail = " "

    # Media
    addTitle(root, "Media")
    media = ET.SubElement(root, "media")
    ET.SubElement(media, "led", id="leds", grid_size="1,1,1")
    ET.SubElement(media, "range_and_bearing", id="ircom")
    ET.SubElement(media, "range_and_bearing", id="rab")
    media.tail = " "

    # Visualization
    addTitle(root, "Visualization")
    visualization = ET.SubElement(root, "visualization")
    visualization.tail = " "

    dom = minidom.parseString(ET.tostring(root))
    with open(file_name, 'w') as file:
        file.write(dom.toprettyxml(indent='  '))
