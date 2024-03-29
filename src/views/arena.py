import math

from PyQt5.QtWidgets import QGroupBox, QGraphicsScene, QGraphicsView, QGraphicsPathItem
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPolygonF, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint, QPointF

from src.models.arena import ArenaShape
from src.util import ResourceLoader, Event, Shape
from src.views.arenaObjects.floor import FloorListView
from src.views.arenaObjects.light import LightListView
from src.views.arenaObjects.obstacle import ObstacleListView
from src.views.arenaObjects.spawn import SpawnView


class ArenaSceneView(QGraphicsScene):
    """
    View of the arena scene itself.
    """
    def __init__(self, graphicsView, *__args):
        super().__init__(*__args)

        self.center = QPointF(0, 0)
        self.areaSize = QPoint(500, 500)
        self.setupScene(graphicsView)

        self.shapePaths = {shape: self.getShapePath(shape) for shape in ArenaShape}  # QGraphicsPathItem
        self.shapeContours = {shape: self.getShapePath(shape) for shape in ArenaShape}
        self.initShapes()

        self.shape = Shape.Dodecagon

    def setupScene(self, graphicsView):
        """
        Initializes the scene.
        """
        self.setSceneRect(-250, -250, 500, 500)
        self.addRect(-250, -250, 500, 500, QPen(Qt.NoPen), QBrush(Qt.black, Qt.Dense2Pattern))
        graphicsView.setScene(self)
        graphicsView.setDragMode(QGraphicsView.NoDrag)
        graphicsView.setRenderHint(QPainter.Antialiasing)

    # ------------ Handling Arena Shape -----------------

    def getShapePath(self, shape):
        """
        Creates a QGraphicsPathItem for the arena depending on the given shape
        """
        path = QPainterPath()

        if shape == Shape.Square:
            path.addRect(-240, -240, 480, 480)
        elif shape == Shape.Circle:
            path.addEllipse(self.center, 240, 240)
        else:
            if shape == Shape.Hexagon:
                n = 6
            elif shape == Shape.Octagon:
                n = 8
            elif shape == Shape.Dodecagon:
                n = 12
            else:
                n = 3

            angle = 360/n
            radius = self.areaSize.x()//2
            points = []
            offset = angle/2 if shape != Shape.Hexagon else 0

            for i in range(n):
                x = self.center.x() + radius * math.cos(math.radians(angle * i + offset))
                y = self.center.y() + radius * math.sin(math.radians(angle * i + offset))
                points.append(QPoint(int(x), int(y)))
            points.append(points[0])
            path.addPolygon(QPolygonF(points))
        return QGraphicsPathItem(path)

    def initShapes(self):
        """
        Setup the brush, color, ... for every of its shape
        """
        for shape in self.shapePaths:
            path = self.shapePaths[shape]
            self.addItem(path)
            path.setBrush(QBrush(QColor(200, 200, 200)))
            pen = QPen(QColor(Qt.black))
            pen.setWidth(3)
            path.setPen(pen)
            path.setVisible(False)

            contour = self.shapeContours[shape]
            self.addItem(contour)
            contour.setPen(pen)
            contour.setZValue(1000)
            contour.setVisible(False)

    def setShape(self, shape):
        """
        Set the current shape of the arena.
        """
        self.setShapeVisibility(self.shape, False)
        self.setShapeVisibility(shape, True)
        self.shape = shape
        self.update()

    def setShapeVisibility(self, shape, visible):
        """
        Set the visibility of a shape to visible or invisble.
        """
        self.shapePaths[shape].setVisible(visible)
        self.shapeContours[shape].setVisible(visible)

    def getArenaPath(self):
        return self.shapePaths[self.shape].path()


class ArenaView(QGroupBox):
    """
    View for arena editor and the arena settings tab.
    """
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ArenaInspector.ui", self)
        self.settingsTab = ResourceLoader.loadWidget("ArenaSettingsTab.ui")

        self.SpawnSettings.layout().setAlignment(Qt.AlignTop)
        self.FloorFrame.layout().setAlignment(Qt.AlignTop)
        self.ObstacleFrame.layout().setAlignment(Qt.AlignTop)
        self.settingsTab.layout().setAlignment(Qt.AlignTop)

        self.ArenaEditSettings.setCurrentIndex(0)

        self.arenaSceneView = ArenaSceneView(self.graphicsView)
        self.spawnView = SpawnView(self)
        self.floorListView = FloorListView(self)
        self.obstacleListView = ObstacleListView(self)
        self.lightListView = LightListView(self)

        self.onArenaClicked = Event()
        self.onArenaSettingsChanged = Event()
        self.onArenaTabChanged = Event()
        self.onArenaPathChanged = Event()
        self.blockSignal = False
        self.connectActions()

    def connectActions(self):
        self.settingsTab.ArenaEditButton.clicked.connect(self.arenaClicked)
        self.settingsTab.Shape.currentIndexChanged.connect(self.shapeChanged)
        self.settingsTab.RobotNumber.valueChanged.connect(self.numberRobotsChanged)
        self.settingsTab.SideLength.valueChanged.connect(self.sideLengthChanged)
        self.ArenaEditSettings.currentChanged.connect(self.onTabChanged)

    def updateView(self, arena):
        """
        Update the view contents with the new arena.
        """
        self.blockSignal = True
        self.arenaSceneView.setShape(arena.shape)
        self.settingsTab.Shape.setCurrentIndex(ArenaShape.index(arena.shape))
        self.settingsTab.RobotNumber.setValue(arena.robotNumber)
        self.settingsTab.SideLength.setValue(arena.sideLength)
        self.blockSignal = False

    def getCenterWidget(self):
        return self

    def getArenaPath(self):
        return self.arenaSceneView.getArenaPath()

    # ---------- Events ------------

    def arenaClicked(self):
        """
        Called when the user clicks on edit arena.
        """
        if self.blockSignal:
            return
        self.onArenaClicked()

    def shapeChanged(self, index):
        if self.blockSignal:
            return
        self.arenaSceneView.setShape(ArenaShape[index])
        self.onArenaPathChanged(self.arenaSceneView.getArenaPath())
        self.onArenaSettingsChanged(shape=ArenaShape[index].name)

    def numberRobotsChanged(self, value):
        if self.blockSignal:
            return
        self.onArenaSettingsChanged(robotNumber=value)

    def sideLengthChanged(self, value):
        if self.blockSignal:
            return
        self.onArenaSettingsChanged(sideLength=value)

    def onTabChanged(self, index):
        self.onArenaTabChanged(index)

    # ------------------------------

    def addSceneItem(self, item):
        """
        Adds a graphic item to the arena scene
        """
        self.arenaSceneView.addItem(item)
        self.arenaSceneView.update()

    def removeSceneItem(self, item):
        """
        Remove a graphic item from the arena scene
        """
        self.arenaSceneView.removeItem(item)
        self.arenaSceneView.update()
