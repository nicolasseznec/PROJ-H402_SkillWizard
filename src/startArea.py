from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPainterPath, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF

from src.itemList import ItemList
from src.util import Event, DataContainer, Shape, Color

StartShape = [Shape.Circle, Shape.Rectangle]  # TODO : ZoneShape


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


# class StartAreaView(QGraphicsPathItem):
class ArenaZone(QGraphicsPathItem):
    def __init__(self, arenaPath, *__args):
        super().__init__(*__args)
        self.setBrush(QBrush(QColor(224, 126, 134, 255)))
        pen = QPen(QColor(Qt.black))
        pen.setWidth(2)
        pen.setStyle(Qt.DashDotLine)
        self.setPen(pen)

        self.onItemChanged = Event()
        self.settingsContainer = None
        self.blockSignal = False

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

        # super(StartAreaView, self).paint(painter, option, widget)
        super(ArenaZone, self).paint(painter, option, widget)

    def getShapePath(self, shape):
        path = QPainterPath()
        if shape == Shape.Rectangle:
            path.addRect(-self.width/2, -self.height/2, self.width, self.height)
        elif shape == Shape.Circle:
            path.addEllipse(-self.radius, -self.radius, self.radius*2, self.radius*2)
        return path

    def setShape(self, shape):
        self.shape = shape

    # def setTabFocus(self, focus):
    #     self.setOpacity(1.0 if focus else 0.3)

    # def connectSettings(self, container):
    #     self.settingsContainer = container
    #     container.StartAreaShape.currentIndexChanged.connect(self.shapeChanged)
    #     container.StartAreaReset.clicked.connect(self.resetPosition)
    #
    #     container.StartAreaRadius.valueChanged.connect(self.radiusChanged)
    #     container.StartAreaWidth.valueChanged.connect(self.widthChanged)
    #     container.StartAreaHeight.valueChanged.connect(self.heightChanged)
    #
    #     container.StartAreaX.valueChanged.connect(self.posXChanged)
    #     container.StartAreaY.valueChanged.connect(self.posYChanged)

    def shapeChanged(self, index):
        if self.blockSignal:
            return
        self.setShape(StartShape[index])
        self.scene().update()
        self.onItemChanged(self.packChanges())

    def resetPosition(self):
        self.setPos(self.scene().center)
        self.onItemChanged(self.packChanges())

    def radiusChanged(self, value):
        if self.blockSignal:
            return
        self.radius = value
        self.updateDimensions(Shape.Circle)
        self.onItemChanged(self.packChanges())

    def widthChanged(self, value):
        if self.blockSignal:
            return
        self.width = value
        self.updateDimensions(Shape.Rectangle)
        self.onItemChanged(self.packChanges())

    def heightChanged(self, value):
        if self.blockSignal:
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

    # def updateProperties(self, startArea):
    #     self.radius = startArea.radius
    #     self.width = startArea.width
    #     self.height = startArea.height
    #     self.shape = Shape[startArea.shape]
    #     self.setPos(startArea.x, startArea.y)
    #     self.updateDimensions()
    #
    #     if self.settingsContainer is None:
    #         return
    #
    #     self.blockSignal = True
    #     self.settingsContainer.StartAreaWidth.setValue(self.width)
    #     self.settingsContainer.StartAreaHeight.setValue(self.height)
    #     self.settingsContainer.StartAreaRadius.setValue(self.radius)
    #     self.settingsContainer.StartAreaShape.setCurrentIndex(StartShape.index(self.shape))
    #     self.blockSignal = False
    #
    # def updateView(self):
    #     if self.settingsContainer is None:
    #         return
    #     self.settingsContainer.StartAreaX.setValue(int(self.x()))
    #     self.settingsContainer.StartAreaY.setValue(int(self.y()))


class StartAreaView(ArenaZone):
    def __init__(self, arenaPath):
        super(StartAreaView, self).__init__(arenaPath)
        self.setZValue(2)

    def setTabFocus(self, focus):
        self.setOpacity(1.0 if focus else 0.3)
        if focus:
            self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def connectSettings(self, container):
        self.settingsContainer = container
        container.StartAreaShape.currentIndexChanged.connect(self.shapeChanged)
        container.StartAreaReset.clicked.connect(self.resetPosition)

        container.StartAreaRadius.valueChanged.connect(self.radiusChanged)
        container.StartAreaWidth.valueChanged.connect(self.widthChanged)
        container.StartAreaHeight.valueChanged.connect(self.heightChanged)

        container.StartAreaX.valueChanged.connect(self.posXChanged)
        container.StartAreaY.valueChanged.connect(self.posYChanged)

    def updateProperties(self, startArea):
        self.radius = startArea.radius
        self.width = startArea.width
        self.height = startArea.height
        self.shape = Shape[startArea.shape]
        self.setPos(startArea.x, startArea.y)
        self.updateDimensions()

        if self.settingsContainer is None:
            return

        self.blockSignal = True
        self.settingsContainer.StartAreaWidth.setValue(self.width)
        self.settingsContainer.StartAreaHeight.setValue(self.height)
        self.settingsContainer.StartAreaRadius.setValue(self.radius)
        self.settingsContainer.StartAreaShape.setCurrentIndex(StartShape.index(self.shape))
        self.blockSignal = False

    def updateView(self):
        if self.settingsContainer is None:
            return
        self.settingsContainer.StartAreaX.setValue(int(self.x()))
        self.settingsContainer.StartAreaY.setValue(int(self.y()))


GrounColor = [Color.Black, Color.Gray, Color.White]


class SpecialGround(StartArea):
    def getAttributes(self):
        attributes = super(SpecialGround, self).getAttributes()
        attributes.update({
            "color": Color.Black.name
        })
        return attributes


class SpecialGroundView(ArenaZone):
    def __init__(self, arenaPath, *__args):
        super().__init__(arenaPath, *__args)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setBrush(QBrush(Qt.white))
        pen = QPen(Qt.NoPen)
        self.setPen(pen)

        self.onSelected = Event()

    def setTabFocus(self, focus):
        if focus:
            self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.setSelected(False)

    def setSelected(self, focus):
        super(SpecialGroundView, self).setSelected(focus)
        if focus:
            self.setPen(Qt.red)
        else:
            self.setPen(QPen(Qt.NoPen))

    def connectSettings(self, container):
        self.settingsContainer = container
        # container.StartAreaShape.currentIndexChanged.connect(self.shapeChanged)
        # container.StartAreaReset.clicked.connect(self.resetPosition)
        #
        # container.StartAreaRadius.valueChanged.connect(self.radiusChanged)
        # container.StartAreaWidth.valueChanged.connect(self.widthChanged)
        # container.StartAreaHeight.valueChanged.connect(self.heightChanged)
        #
        # container.StartAreaX.valueChanged.connect(self.posXChanged)
        # container.StartAreaY.valueChanged.connect(self.posYChanged)

    def updateProperties(self, ground):
        # self.radius = startArea.radius
        # self.width = startArea.width
        # self.height = startArea.height
        # self.shape = Shape[startArea.shape]
        # self.setPos(startArea.x, startArea.y)
        self.updateDimensions()

        if self.settingsContainer is None:
            return

        self.blockSignal = True
        # self.settingsContainer.StartAreaWidth.setValue(self.width)
        # self.settingsContainer.StartAreaHeight.setValue(self.height)
        # self.settingsContainer.StartAreaRadius.setValue(self.radius)
        # self.settingsContainer.StartAreaShape.setCurrentIndex(StartShape.index(self.shape))
        self.blockSignal = False

    def updateView(self):
        if self.settingsContainer is None:
            return
        # self.settingsContainer.StartAreaX.setValue(int(self.x()))
        # self.settingsContainer.StartAreaY.setValue(int(self.y()))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.onSelected(self)

        return super(SpecialGroundView, self).itemChange(change, value)


class SpecialGroundList(ItemList):
    def createNewItem(self):
        item = SpecialGroundView(self.arenaPath)
        item.onSelected += self.selectItem
        return item

    def handleRemoval(self, item):
        item.onSelected -= self.selectItem

    def getDefaultName(self):
        return "New Floor"

    def setArenaPath(self, arenaPath):
        self.arenaPath = arenaPath
        for item in self.items:
            item.arenaPath = arenaPath

    def getWidgets(self, container):
        self.listWidget = container.GroundList
        self.addButton = container.GroundAdd
        self.removeButton = container.GroundRemove

    def unselectAll(self):
        for item in self.items:
            item.setSelected(False)

    def setTabFocus(self, focus):
        for item in self.items:
            item.setTabFocus(focus)

        if focus and self.listWidget.currentRow() >= 0:
            self.onItemSelected(self.items[self.listWidget.currentRow()])

    def selectItem(self, item):
        index = self.items.index(item)
        self.listWidget.setCurrentRow(index)
