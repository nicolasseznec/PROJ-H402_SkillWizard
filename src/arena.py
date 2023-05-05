from enum import Enum
import math

from PyQt5.QtWidgets import QGroupBox, QFrame, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsView, \
    QGraphicsPathItem
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPolygonF, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint, QPointF

from src.util import ResourceLoader, Event


class ArenaShape(Enum):
    Square = 1
    Hexagon = 2
    Octagon = 3
    Dodecagon = 4
    Circle = 5


# Holds the parameters values
class Arena:
    def __init__(self):
        self.shape = ArenaShape.Square
        # self.sideLength = 66


class MyEllipseItem(QGraphicsEllipseItem):
    def itemChange(self, change, value):

        # if change == QGraphicsItem.ItemPositionChange:
        # print("New position:", self.scenePos().x(), self.scenePos().y())
        #     print("New position:", value)

        return super().itemChange(change, value)


class ArenaRenderArea(QGraphicsScene):    # Handles Arena graphics
    def __init__(self, *__args):
        super().__init__(*__args)
        self.areaSize = QPoint(500, 500)
        self.center = QPointF(0, 0)
        self.shape = ArenaShape.Dodecagon
        self.setSceneRect(-250, -250, 500, 500)

        self.shapePaths = {shape: self.getShapePath(shape) for shape in ArenaShape}  # QGraphicsPathItem
        self.initShapes()

        # Add some items to the scene
        # pen = QPen()
        # pen.setWidth(3)
        # self.ellipse_item: QGraphicsItem = self.addEllipse(50, 50, 200, 100, pen, QBrush(QColor(255, 255, 0)))
        # self.ellipse_item: QGraphicsItem = MyEllipseItem(0, 0, 200, 100)
        # self.ellipse_item.setPen(pen)
        # self.ellipse_item.setBrush(QBrush(QColor(0, 0, 255)))
        # self.ellipse_item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        # self.addItem(self.ellipse_item)

        # line_item = self.addLine(0, 0, 500, 500, pen)
        # line_item.setPen(QPen(QColor(255, 0, 0), 5))

    def getShapePath(self, shape):
        path = QPainterPath()

        if shape == ArenaShape.Square:
            path.addRect(-240, -240, 480, 480)
        elif shape == ArenaShape.Circle:
            path.addEllipse(self.center, 240, 240)
        else:
            if shape == ArenaShape.Hexagon:
                n = 6
            elif shape == ArenaShape.Octagon:
                n = 8
            elif shape == ArenaShape.Dodecagon:
                n = 12
            else:
                n = 3

            angle = 360/n
            radius = self.areaSize.x()//2
            points = []

            for i in range(n):
                x = self.center.x() + radius * math.cos(math.radians(angle * (i + 0.5)))
                y = self.center.y() + radius * math.sin(math.radians(angle * (i + 0.5)))
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
        self.shape = shape
        self.update()


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
        self.graphicsView.setScene(self.arenaRenderArea)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)

    def getCenterWidget(self):
        return self

    def arenaClicked(self):
        self.onArenaClicked()

    def shapeChanged(self, index):
        newShape = ArenaShape(index+1)
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
