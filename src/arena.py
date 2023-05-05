from enum import Enum
import math

from PyQt5.QtWidgets import QGroupBox, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsView, \
    QGraphicsPathItem
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPolygonF, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint, QPointF

from src.util import ResourceLoader, Event


class Shape(Enum):
    Square = 1
    Hexagon = 2
    Octagon = 3
    Dodecagon = 4
    Circle = 5
    Rectangle = 6


ArenaShape = [Shape(i) for i in range(1, 6)]
StartShape = [Shape.Circle, Shape.Rectangle]


# Holds the parameters values
class Arena:
    def __init__(self):
        self.shape = Shape.Square
        # self.sideLength = 66


class StartArea(QGraphicsPathItem):
    def __init__(self, arenaPath, *__args):
        super().__init__(*__args)
        self.setBrush(QBrush(QColor(224, 126, 134, 255)))
        pen = QPen(QColor(Qt.black))
        pen.setWidth(3)
        pen.setStyle(Qt.DashDotLine)
        self.setPen(pen)

        self.radius = 50
        self.width = 100
        self.height = 100
        self.setShape(Shape.Circle)
        self.updateDimensions()

        self.arenaPath = arenaPath

    def paint(self, painter, option, widget=None):
        intersect = self.arenaPath.intersected(self.shapePaths[self.shape].translated(self.scenePos())) \
            .translated(-self.scenePos())
        intersect.closeSubpath()
        self.setPath(intersect)
        super(StartArea, self).paint(painter, option, widget)

    def getShapePath(self, shape):
        path = QPainterPath()
        if shape == Shape.Rectangle:
            path.addRect(-self.width/2, -self.height/2, self.width, self.height)
        elif shape == Shape.Circle:
            path.addEllipse(-self.radius, -self.radius, self.radius*2, self.radius*2)
        return path

    def setShape(self, shape):
        self.shape = shape

    def setPosition(self, pos):
        self.setPos(pos)

    def setTabFocus(self, focus):
        self.setOpacity(1.0 if focus else 0.4)

    def connectSettings(self, container):
        container.StartAreaShape.currentIndexChanged.connect(self.startAreaShapeChanged)
        container.StartAreaReset.clicked.connect(self.resetStartArea)

        container.StartAreaRadius.valueChanged.connect(self.radiusChanged)
        container.StartAreaWidth.valueChanged.connect(self.widthChanged)
        container.StartAreaHeight.valueChanged.connect(self.heightChanged)

    def startAreaShapeChanged(self, index):
        self.setShape(StartShape[index])
        self.scene().update()

    def resetStartArea(self):
        self.setPosition(self.scene().center)

    def radiusChanged(self, value):
        self.radius = value
        self.updateDimensions(Shape.Circle)

    def widthChanged(self, value):
        self.width = value
        self.updateDimensions(Shape.Rectangle)

    def heightChanged(self, value):
        self.height = value
        self.updateDimensions(Shape.Rectangle)

    def updateDimensions(self, shape=None):
        if shape is not None:
            self.shapePaths[shape] = self.getShapePath(shape)
        else:
            self.shapePaths = {s: self.getShapePath(s) for s in StartShape}  # QGraphicsPathItem

        scene = self.scene()
        if scene is not None:
            scene.update()


class ArenaRenderArea(QGraphicsScene):    # Handles Arena graphics
    def __init__(self, *__args):
        super().__init__(*__args)
        self.areaSize = QPoint(500, 500)
        self.center = QPointF(0, 0)
        self.shape = Shape.Dodecagon
        self.setSceneRect(-250, -250, 500, 500)

        self.shapePaths = {shape: self.getShapePath(shape) for shape in ArenaShape}  # QGraphicsPathItem
        self.initShapes()

        self.startArea = StartArea(self.shapePaths[self.shape].path())
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
            path.setPen(QPen(QColor(Qt.black)))
            path.setVisible(False)

        self.shapePaths[self.shape].setVisible(True)

    def setShape(self, shape):
        self.shapePaths[self.shape].setVisible(False)
        self.shapePaths[shape].setVisible(True)
        self.startArea.arenaPath = self.shapePaths[shape].path()
        self.shape = shape
        self.update()

    def connectSettings(self, container):
        self.startArea.connectSettings(container)
        container.ArenaEditSettings.currentChanged.connect(self.onTabChange)

    def onTabChange(self, index):
        self.startArea.setTabFocus(index == 0)


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


class ArenaController:
    def __init__(self):
        self.view = ArenaView()
        self.onArenaSelected = Event()

        self.view.onArenaClicked += self.onArenaClicked

    def getView(self):
        return self.view

    def getTab(self):
        return self.view.settingsTab

    def setSelected(self, selected):
        pass

    def onArenaClicked(self):
        self.onArenaSelected(self)
