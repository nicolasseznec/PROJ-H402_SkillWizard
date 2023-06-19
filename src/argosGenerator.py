import math
from xml.dom import minidom
import xml.etree.ElementTree as ET

from src.mission import Mission, Arena
from src.util import Shape
from src.light import Light


def addTitle(element, title):
    titleStr = ' * ' + title + ' * '
    line = ' ' + '*' * (len(titleStr) - 2) + ' '

    element.append(ET.Comment(line))
    element.append(ET.Comment(titleStr))
    element.append(ET.Comment(line))


def addComment(element, comment):
    element.append(ET.Comment(" " + comment + " "))


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
    # TODO : Square, Circle shapes
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


def addLight(element, light, coord_scale, id_=0):
    # TODO : Points lights
    color = light.color.lower()
    angle = "{},0,0".format(light.orientation)
    pos = "{},{},0".format(light.x * coord_scale, light.y * coord_scale)
    intensity = str(round(light.strength/10, 2))

    ET.SubElement(element, "light", id="light_" + str(id_), position=pos, orientation=angle, color=color, intensity=intensity, medium="leds")


def addFloor(element, floors):
    # TODO : Generate a picture from the floors
    addComment(element, "TO COMPLETE ! : User needs to complete some of the following fields")
    ET.SubElement(element, "floor", id="floor", source="image", path="PATH_TO_FLOOR_IMAGE")


def addObstacle(element, obstacle, coord_scale, id_=0):
    # TODO : circle shape
    angle = (obstacle.orientation, 0, 0)
    size = (obstacle.width * coord_scale, obstacle.height * coord_scale, 0.08)
    pos = (obstacle.x * coord_scale, obstacle.y * coord_scale, 0)
    addBox(element, "obstacle_" + str(id_), size=size, position=pos, orientation=angle)


def generateArena(arena: Arena, element):
    arenaElement = ET.SubElement(element, "arena", size="10, 10, 1", center="0,0,0")
    addComment(arenaElement, "{} arena with side of length {}".format(arena.shape, arena.sideLength))
    generateArenaBorders(arena, arenaElement)

    addComment(arenaElement, "Arena floor")
    addFloor(arenaElement, arena.floors)

    coord_scale = arena.sideLength / 250
    addComment(arenaElement, "Arena lights")
    if not arena.lights:
        addLight(arenaElement, Light.dummyLight(), 0, 0)
    for l_id, light in enumerate(arena.lights):
        addLight(arenaElement, light, coord_scale, l_id)

    addComment(arenaElement, "Arena obstacles")
    for o_id, obstacle in enumerate(arena.obstacles):
        addObstacle(arenaElement, obstacle, coord_scale, o_id)

    arenaElement.tail = " "


# sensors
controller_input = {
    "prox": ET.Element("epuck_proximity", implementation="default", show_rays="false", noise_level="0.05", calibrated="true"),
    "gnd": ET.Element("epuck_ground", implementation="rot_z_only", noise_level="0.05", calibrated="true"),
    "light": ET.Element("epuck_light", implementation="default", show_rays="false", noise_level="0.05", calibrated="true"),
    "cam": ET.Element("epuck_omnidirectional_camera", implementation="rot_z_only", medium="leds", show_rays="false")
}

# actuators
controller_output = {
    "wheels": ET.Element("epuck_wheels", implementation="default", noise_std_dev="0.05"),
    "leds": ET.Element("epuck_rgb_leds", implementation="default", medium="leds"),
}


def generateController(mission, element):
    # TODO : controllers
    controllers = ET.SubElement(element, "controllers")
    controllers.tail = " "

    addComment(controllers, "TRANSMITTER")
    addComment(controllers, "TO COMPLETE ! : User needs to complete some of the following fields")
    automode = ET.SubElement(controllers, "automode_controller", id="automode", library="PATH_TO_AUTOMODE")

    actuators = ET.SubElement(automode, "actuators")
    for elem in mission.reference_model.outputs:
        if elem in controller_output:
            actuators.append(controller_output[elem])
    ET.SubElement(actuators, "epuck_range_and_bearing", implementation="medium", medium="rab", data_size="4", range="0.7")

    sensors = ET.SubElement(automode, "sensors")
    for elem in mission.reference_model.inputs:
        if elem in controller_input:
            sensors.append(controller_input[elem])
    ET.SubElement(sensors, "epuck_range_and_bearing", implementation="medium", medium="rab", data_size="4", nois_std_deviation="1.5", loss_probability="0.85", calibrated="true")

    fsm_config = "TO_COMPLETE"  # TODO : FSM config
    params = ET.SubElement(automode, "params", attrib={"readable": "false", "history": "false", "hist-folder": "./fsm_history/", "fsm-config": fsm_config})


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
    addComment(root, "TO COMPLETE ! : User needs to complete some of the following fields")
    loop_functions = ET.SubElement(root, "loop_functions", library="PATH_TO_LOOP_FUNCTION", label="LOOP_FUNCTIONS_LABEL")
    ET.SubElement(loop_functions, "params", dist_radius="1.2", number_robots=str(mission.arena.robotNumber))
    loop_functions.tail = " "

    # Controllers
    addTitle(root, "Controllers")
    generateController(mission, root)

    # Arena
    addTitle(root, "Arena")
    generateArena(mission.arena, root)

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
