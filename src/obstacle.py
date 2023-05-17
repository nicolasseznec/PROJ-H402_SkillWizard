from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QColor, QPainterPath, QPen, QBrush
from PyQt5.QtCore import Qt

from src.startArea import StartArea, MultiArenaZone, StartShape, ArenaList
from src.util import Event, Shape


class Obstacle(StartArea):
    def getAttributes(self):
        attributes = super(Obstacle, self).getAttributes()
        attributes.update({
            "orientation": 0
        })
        return attributes


class ObstacleView(MultiArenaZone):
    def __init__(self, arenaPath, *__args):
        super().__init__(arenaPath, *__args)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setZValue(1)

        brush = QBrush(Qt.black, Qt.Dense2Pattern)
        self.setBrush(brush)
        pen = QPen(Qt.gray)
        pen.setWidth(2)
        self.setPen(pen)

        self.orientation = 0
        self.name = "New Obstacle"
        self.onSelected = Event()

    def connectSettings(self, container):
        if container is None:
            return
        self.settingsContainer = container
        container.ObstacleShape.currentIndexChanged.connect(self.shapeChanged)
        container.ObstacleReset.clicked.connect(self.resetPosition)

        container.ObstacleRadius.valueChanged.connect(self.radiusChanged)
        container.ObstacleWidth.valueChanged.connect(self.widthChanged)
        container.ObstacleHeight.valueChanged.connect(self.heightChanged)

        container.ObstacleX.valueChanged.connect(self.posXChanged)
        container.ObstacleY.valueChanged.connect(self.posYChanged)

    def disconnectSettings(self):
        if self.settingsContainer is None:
            return

        self.settingsContainer.ObstacleShape.currentIndexChanged.disconnect(self.shapeChanged)
        self.settingsContainer.ObstacleReset.clicked.disconnect(self.resetPosition)

        self.settingsContainer.ObstacleRadius.valueChanged.disconnect(self.radiusChanged)
        self.settingsContainer.ObstacleWidth.valueChanged.disconnect(self.widthChanged)
        self.settingsContainer.ObstacleHeight.valueChanged.disconnect(self.heightChanged)

        self.settingsContainer.ObstacleX.valueChanged.disconnect(self.posXChanged)
        self.settingsContainer.ObstacleY.valueChanged.disconnect(self.posYChanged)

    def orientationChanged(self, value):
        if self.blockSignal:
            return
        self.orientation = value
        self.updateDimensions(Shape.Rectangle)
        self.onItemChanged(self.packChanges())

    def updateProperties(self, ground):
        # self.radius = startArea.radius
        # self.width = startArea.width
        # self.height = startArea.height
        # self.shape = Shape[startArea.shape]
        # self.setPos(startArea.x, startArea.y)
        # self name =
        # self.orientation = 
        self.updateDimensions()
        self.updateView()

    def updateView(self):
        if self.settingsContainer is None:
            return

        self.blockSignal = True
        self.settingsContainer.ObstacleWidth.setValue(self.width)
        self.settingsContainer.ObstacleHeight.setValue(self.height)
        self.settingsContainer.ObstacleRadius.setValue(self.radius)
        self.settingsContainer.ObstacleShape.setCurrentIndex(StartShape.index(self.shape))
        self.updatePos()
        self.blockSignal = False

    def updatePos(self):
        super(ObstacleView, self).updatePos()
        self.settingsContainer.ObstacleX.setValue(int(self.x()))
        self.settingsContainer.ObstacleY.setValue(int(self.y()))


class ObstacleList(ArenaList):
    def itemFactory(self, arenaPath, model=None):
        return ObstacleView(self.arenaPath)

    def getDefaultName(self):
        return "New Obstacle"

    def getWidgets(self, container):
        self.listWidget = container.ObstacleList
        self.addButton = container.ObstacleAdd
        self.removeButton = container.ObstacleRemove
