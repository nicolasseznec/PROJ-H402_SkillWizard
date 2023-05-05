from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QColor, QPainterPath, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF

from src.util import Event, DataContainer, Shape

StartShape = [Shape.Circle, Shape.Rectangle]


class StartArea(DataContainer):
    def getAttributes(self):
        return {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100,
            "radius": 50,
            "shape": Shape.Circle.name
        }


class StartAreaView(QGraphicsPathItem):
    def __init__(self, arenaPath, *__args):
        super().__init__(*__args)
        self.setBrush(QBrush(QColor(224, 126, 134, 255)))
        pen = QPen(QColor(Qt.black))
        pen.setWidth(2)
        pen.setStyle(Qt.DashDotLine)
        self.setPen(pen)

        self.onItemChanged = Event()
        self.settingsContainer = None
        self.blockSignals = False

        self.prev_pos = QPointF(0, 0)
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
        if self.scenePos() != self.prev_pos:
            self.prev_pos = self.scenePos()
            self.updateView()

        super(StartAreaView, self).paint(painter, option, widget)

    def getShapePath(self, shape):
        path = QPainterPath()
        if shape == Shape.Rectangle:
            path.addRect(-self.width/2, -self.height/2, self.width, self.height)
        elif shape == Shape.Circle:
            path.addEllipse(-self.radius, -self.radius, self.radius*2, self.radius*2)
        return path

    def setShape(self, shape):
        self.shape = shape

    def setTabFocus(self, focus):
        self.setOpacity(1.0 if focus else 0.3)

    def connectSettings(self, container):
        self.settingsContainer = container
        container.StartAreaShape.currentIndexChanged.connect(self.startAreaShapeChanged)
        container.StartAreaReset.clicked.connect(self.resetStartArea)

        container.StartAreaRadius.valueChanged.connect(self.radiusChanged)
        container.StartAreaWidth.valueChanged.connect(self.widthChanged)
        container.StartAreaHeight.valueChanged.connect(self.heightChanged)

        container.StartAreaX.valueChanged.connect(self.posXChanged)
        container.StartAreaY.valueChanged.connect(self.posYChanged)

    def startAreaShapeChanged(self, index):
        if self.blockSignals:
            return
        self.setShape(StartShape[index])
        self.scene().update()
        self.onItemChanged(self.packChanges())

    def resetStartArea(self):
        self.setPos(self.scene().center)
        self.onItemChanged(self.packChanges())

    def radiusChanged(self, value):
        if self.blockSignals:
            return
        self.radius = value
        self.updateDimensions(Shape.Circle)
        self.onItemChanged(self.packChanges())

    def widthChanged(self, value):
        if self.blockSignals:
            return
        print(value)
        self.width = value
        self.updateDimensions(Shape.Rectangle)
        self.onItemChanged(self.packChanges())

    def heightChanged(self, value):
        if self.blockSignals:
            return
        self.height = value
        self.updateDimensions(Shape.Rectangle)
        self.onItemChanged(self.packChanges())

    def updateDimensions(self, shape=None):
        if shape is not None:
            self.shapePaths[shape] = self.getShapePath(shape)
        else:
            self.shapePaths = {s: self.getShapePath(s) for s in StartShape}  # QGraphicsPathItem

        scene = self.scene()
        if scene is not None:
            scene.update()

    def posXChanged(self, value):
        self.setX(value)
        self.onItemChanged(self.packChanges())

    def posYChanged(self, value):
        self.setY(value)
        self.onItemChanged(self.packChanges())

    def packChanges(self):
        return {
            "radius": self.radius,
            "width": self.width,
            "height": self.height,
            "x": int(self.x()),
            "y": int(self.y()),
            "shape": self.shape.name
        }

    def updateProperties(self, startArea):
        self.radius = startArea.radius
        self.width = startArea.width
        self.height = startArea.height
        self.shape = Shape[startArea.shape]
        self.setPos(startArea.x, startArea.y)
        self.updateDimensions()

        if self.settingsContainer is None:
            return

        self.blockSignals = True
        self.settingsContainer.StartAreaWidth.setValue(self.width)
        self.settingsContainer.StartAreaHeight.setValue(self.height)
        self.settingsContainer.StartAreaRadius.setValue(self.radius)
        self.settingsContainer.StartAreaShape.setCurrentIndex(StartShape.index(self.shape))
        self.blockSignals = False

    def updateView(self):
        if self.settingsContainer is None:
            return
        self.settingsContainer.StartAreaX.setValue(int(self.x()))
        self.settingsContainer.StartAreaY.setValue(int(self.y()))
