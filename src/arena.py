import math

from PyQt5.QtWidgets import QGroupBox, QGraphicsScene, QGraphicsItem, QGraphicsView, \
    QGraphicsPathItem
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPolygonF, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint, QPointF

from src.util import ResourceLoader, Event, Shape
from src.startArea import StartArea, StartAreaView, SpecialGroundList

ArenaShape = [Shape(i) for i in range(1, 6)]


# Holds the parameters values
class Arena:
    def __init__(self, data=None):
        self.shape = Shape.Square.name

        if data is None:
            data = {}
        self.loadFromData(data)

        # self.sideLength = 66

    def loadFromData(self, data, updateStartArea=True):
        self.shape = Shape.Dodecagon.name if "shape" not in data else data["shape"]
        if updateStartArea:
            self.startArea = StartArea({} if "StartArea" not in data else data["StartArea"])

    def toJson(self):
        return {
            "shape": self.shape,
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
        self.shapeContours = {shape: self.getShapePath(shape) for shape in ArenaShape}
        self.initShapes()

        self.groundList = SpecialGroundList()
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

        self.shapePaths[self.shape].setVisible(True)
        self.shapeContours[self.shape].setVisible(True)

    def setShape(self, shape):
        self.shapePaths[self.shape].setVisible(False)
        self.shapeContours[self.shape].setVisible(False)
        self.shapePaths[shape].setVisible(True)
        self.shapeContours[shape].setVisible(True)

        self.startArea.arenaPath = self.shapePaths[shape].path()
        self.groundList.setArenaPath(self.shapePaths[shape].path())
        self.shape = shape
        self.update()

    def connectSettings(self, container):
        self.settingsContainer = container
        self.startArea.connectSettings(container)
        container.ArenaEditSettings.currentChanged.connect(self.onTabChange)

        self.groundList.connectWidgets(container)
        self.groundList.onItemSelected += self.onItemSelected
        self.groundList.onItemRemoved += self.onItemRemoved
        self.groundList.onItemAdded += self.onItemAdded

    def onTabChange(self, index):
        self.startArea.setTabFocus(index == 0)
        self.groundList.setTabFocus(index == 1)

    def updateView(self, arena):
        self.setShape(Shape[arena.shape])
        self.startArea.updateProperties(arena.startArea)

    def onItemSelected(self, item):
        self.groundList.unselectAll()
        item.setSelected(True)

    def onItemRemoved(self, item):
        self.removeItem(item)
        self.update()

    def onItemAdded(self, item):
        self.addItem(item)
        item.setSelected(True)
        self.update()


class ArenaView(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ArenaInspector.ui", self)

        self.settingsTab = ResourceLoader.loadWidget("ArenaSettingsTab.ui")
        self.settingsTab.layout().setAlignment(Qt.AlignTop)

        self.ArenaEditSettings.setCurrentIndex(0)

        self.blockSignal = False
        self.settingsTab.ArenaEditButton.clicked.connect(self.arenaClicked)
        self.settingsTab.Shape.currentIndexChanged.connect(self.shapeChanged)
        self.onArenaClicked = Event()

        self.arenaRenderArea = ArenaRenderArea()
        self.arenaRenderArea.connectSettings(self)
        self.graphicsView.setScene(self.arenaRenderArea)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)

        self.onArenaSettingsChanged = Event()

    def getCenterWidget(self):
        return self

    def arenaClicked(self):
        self.onArenaClicked()

    def shapeChanged(self, index):
        if self.blockSignal:
            return
        newShape = ArenaShape[index]
        self.arenaRenderArea.setShape(newShape)

        self.onArenaSettingsChanged(self.packChanges())

    def updateView(self, arena):
        self.arenaRenderArea.updateView(arena)

        self.blockSignal = True
        self.settingsTab.Shape.setCurrentIndex(ArenaShape.index(self.arenaRenderArea.shape))
        self.blockSignal = False

    def packChanges(self):
        return {
            "shape": self.arenaRenderArea.shape.name
        }


class ArenaController:
    def __init__(self, arena=None):
        self.setArena(arena)
        self.view = ArenaView()
        self.onArenaSelected = Event()

        self.view.onArenaClicked += self.onArenaClicked
        self.view.onArenaSettingsChanged += self.onSettingsChanged
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

    def onSettingsChanged(self, values):
        if self.arena is not None:
            self.arena.loadFromData(values, updateStartArea=False)
