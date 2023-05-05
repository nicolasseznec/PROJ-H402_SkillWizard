import math

from PyQt5.QtWidgets import QGroupBox, QGraphicsScene, QGraphicsItem, QGraphicsView, \
    QGraphicsPathItem
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPolygonF, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint, QPointF

from src.util import ResourceLoader, Event, Shape
from src.startArea import StartArea, StartAreaView

ArenaShape = [Shape(i) for i in range(1, 6)]


# Holds the parameters values
class Arena:
    def __init__(self, data=None):
        self.shape = Shape.Square

        if data is None:
            data = {}
        self.loadFromData(data)

        # self.sideLength = 66

    def loadFromData(self, data):
        self.startArea = StartArea({} if "StartArea" not in data else data["StartArea"])

    def toJson(self):
        return {
            "StartArea": self.startArea.toJson()
        }


class ArenaRenderArea(QGraphicsScene):    # Handles Arena graphics
    def __init__(self, *__args):
        super().__init__(*__args)
        self.areaSize = QPoint(500, 500)
        self.center = QPointF(0, 0)
        self.shape = Shape.Dodecagon
        self.setSceneRect(-250, -250, 500, 500)

        self.shapePaths = {shape: self.getShapePath(shape) for shape in ArenaShape}  # QGraphicsPathItem
        self.initShapes()

        self.startArea = StartAreaView(self.shapePaths[self.shape].path())
        self.startArea.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.addItem(self.startArea)

    def getShapePath(self, shape):
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
        for path in self.shapePaths.values():
            self.addItem(path)
            path.setBrush(QBrush(QColor(200, 200, 200)))
            pen = QPen(QColor(Qt.black))
            pen.setWidth(3)
            path.setPen(pen)
            path.setVisible(False)

        self.shapePaths[self.shape].setVisible(True)

    def setShape(self, shape):
        self.shapePaths[self.shape].setVisible(False)
        self.shapePaths[shape].setVisible(True)
        self.startArea.arenaPath = self.shapePaths[shape].path()
        self.shape = shape
        self.update()

    def connectSettings(self, container):
        self.settingsContainer = container
        self.startArea.connectSettings(container)
        container.ArenaEditSettings.currentChanged.connect(self.onTabChange)

    def onTabChange(self, index):
        self.startArea.setTabFocus(index == 0)

    def updateView(self, arena):
        self.startArea.updateProperties(arena.startArea)


class ArenaView(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ArenaInspector.ui", self)

        self.settingsTab = ResourceLoader.loadWidget("ArenaSettingsTab.ui")
        self.settingsTab.layout().setAlignment(Qt.AlignTop)

        self.settingsTab.ArenaEditButton.clicked.connect(self.arenaClicked)
        self.settingsTab.Shape.currentIndexChanged.connect(self.shapeChanged)
        self.onArenaClicked = Event()

        self.arenaRenderArea = ArenaRenderArea()
        self.arenaRenderArea.connectSettings(self)
        self.graphicsView.setScene(self.arenaRenderArea)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)

    def getCenterWidget(self):
        return self

    def arenaClicked(self):
        self.onArenaClicked()

    def shapeChanged(self, index):
        newShape = ArenaShape[index]
        # TODO : notify controller to update Arena model
        self.arenaRenderArea.setShape(newShape)

    def updateView(self, arena):
        self.arenaRenderArea.updateView(arena)


class ArenaController:
    def __init__(self, arena=None):
        self.setArena(arena)
        self.view = ArenaView()
        self.onArenaSelected = Event()

        self.view.onArenaClicked += self.onArenaClicked
        self.view.arenaRenderArea.startArea.onItemChanged += self.onStartAreaChanged

    def getView(self):
        return self.view

    def getTab(self):
        return self.view.settingsTab

    def setSelected(self, selected):
        pass

    def onArenaClicked(self):
        self.onArenaSelected(self)

    def setArena(self, arena):
        self.arena = arena

        if arena is not None:
            self.view.updateView(arena)

    def onStartAreaChanged(self, values):
        if self.arena is not None:
            self.arena.startArea.loadFromData(values)
