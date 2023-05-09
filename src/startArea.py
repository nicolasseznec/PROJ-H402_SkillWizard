from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QDialog
from PyQt5.QtGui import QColor, QPainterPath, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF

from src.itemList import ItemList, TextDialog
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
            self.updatePos()

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

    def shapeChanged(self, index):
        if self.blockSignal:
            return
        self.setShape(StartShape[index])
        self.scene().update()
        self.onItemChanged(self.packChanges())

    def resetPosition(self):
        if self.blockSignal:
            return
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
        if self.blockSignal:
            return
        self.setX(value)
        self.onItemChanged(self.packChanges())

    def posYChanged(self, value):
        if self.blockSignal:
            return
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

    def updatePos(self):
        if self.settingsContainer is None:
            return


class StartAreaView(ArenaZone):
    def __init__(self, arenaPath):
        super(StartAreaView, self).__init__(arenaPath)
        self.setZValue(2)

    def setTabFocus(self, focus):
        self.setOpacity(0.9 if focus else 0.3)
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

    def updatePos(self):
        super(StartAreaView, self).updatePos()
        self.settingsContainer.StartAreaX.setValue(int(self.x()))
        self.settingsContainer.StartAreaY.setValue(int(self.y()))


class MultiArenaZone(ArenaZone):
    def __init__(self, arenaPath, *__args):
        super().__init__(arenaPath, *__args)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.onSelected = Event()

    def setTabFocus(self, focus):
        if focus:
            self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.setSelected(False)

    def setSelected(self, focus):
        super(MultiArenaZone, self).setSelected(focus)
        if focus:
            self.blockSignal = False
            self.updateView()
        else:
            self.blockSignal = True

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.onSelected(self)

        return super(MultiArenaZone, self).itemChange(change, value)


GrounColor = [Color.Black, Color.Gray, Color.White]


class SpecialGround(StartArea):
    def getAttributes(self):
        attributes = super(SpecialGround, self).getAttributes()
        attributes.update({
            "color": Color.Black.name
        })
        return attributes


class SpecialGroundView(MultiArenaZone):
    def __init__(self, arenaPath, *__args):
        super().__init__(arenaPath, *__args)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setBrush(QBrush(Qt.black))
        pen = QPen(Qt.NoPen)
        self.setPen(pen)

        self.color = Color.Black
        self.name = "New Floor"
        self.onSelected = Event()

    def connectSettings(self, container):
        if container is None:
            return
        self.settingsContainer = container
        container.GroundShape.currentIndexChanged.connect(self.shapeChanged)
        container.GroundColor.currentIndexChanged.connect(self.colorChanged)
        container.GroundReset.clicked.connect(self.resetPosition)

        container.GroundRadius.valueChanged.connect(self.radiusChanged)
        container.GroundWidth.valueChanged.connect(self.widthChanged)
        container.GroundHeight.valueChanged.connect(self.heightChanged)

        container.GroundX.valueChanged.connect(self.posXChanged)
        container.GroundY.valueChanged.connect(self.posYChanged)

    def disconnectSettings(self):
        if self.settingsContainer is None:
            return

        self.settingsContainer.GroundShape.currentIndexChanged.disconnect(self.shapeChanged)
        self.settingsContainer.GroundColor.currentIndexChanged.disconnect(self.colorChanged)
        self.settingsContainer.GroundReset.clicked.disconnect(self.resetPosition)

        self.settingsContainer.GroundRadius.valueChanged.disconnect(self.radiusChanged)
        self.settingsContainer.GroundWidth.valueChanged.disconnect(self.widthChanged)
        self.settingsContainer.GroundHeight.valueChanged.disconnect(self.heightChanged)

        self.settingsContainer.GroundX.valueChanged.disconnect(self.posXChanged)
        self.settingsContainer.GroundY.valueChanged.disconnect(self.posYChanged)

    def colorChanged(self, index):
        if self.blockSignal:
            return
        self.color = GrounColor[index]

        if self.color == Color.Black:
            self.setBrush(QBrush(Qt.black))
        elif self.color == Color.White:
            self.setBrush(QBrush(Qt.white))
        elif self.color == Color.Gray:
            self.setBrush(QBrush(Qt.gray))

        self.scene().update()
        self.onItemChanged(self.packChanges())

    def updateProperties(self, ground):
        # self.radius = startArea.radius
        # self.width = startArea.width
        # self.height = startArea.height
        # self.shape = Shape[startArea.shape]
        # self.setPos(startArea.x, startArea.y)
        # self name =
        self.updateDimensions()
        self.updateView()

    def updateView(self):
        if self.settingsContainer is None:
            return

        self.blockSignal = True
        self.settingsContainer.GroundWidth.setValue(self.width)
        self.settingsContainer.GroundHeight.setValue(self.height)
        self.settingsContainer.GroundRadius.setValue(self.radius)
        self.settingsContainer.GroundShape.setCurrentIndex(StartShape.index(self.shape))
        self.settingsContainer.GroundColor.setCurrentIndex(GrounColor.index(self.color))
        self.updatePos()
        self.blockSignal = False

    def updatePos(self):
        super(SpecialGroundView, self).updatePos()
        self.settingsContainer.GroundX.setValue(int(self.x()))
        self.settingsContainer.GroundY.setValue(int(self.y()))


class ArenaList(ItemList):
    def createNewItem(self):
        item: MultiArenaZone = self.itemFactory(self.arenaPath)
        item.onSelected += self.selectItem
        item.connectSettings(self.container)
        return item

    def itemFactory(self, arenaPath):
        return MultiArenaZone(arenaPath)

    def handleRemoval(self, item):
        item.onSelected -= self.selectItem
        item.disconnectSettings()

    def setArenaPath(self, arenaPath):
        self.arenaPath = arenaPath
        for item in self.items:
            item.arenaPath = arenaPath

    def connectWidgets(self, container):
        super(ArenaList, self).connectWidgets(container)
        for item in self.items:
            item.connectSettings(container)

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

    def onItemDoubleClicked(self, item):
        index = self.listWidget.row(item)
        dialog = TextDialog(self.listWidget, item.text(), "Change name")
        if dialog.exec_() == QDialog.Accepted:
            line_edit_value = dialog.getLineEditValue()
            if line_edit_value:
                item.setText(line_edit_value)
                self.items[index].name = line_edit_value


class SpecialGroundList(ArenaList):
    def itemFactory(self, arenaPath):
        return SpecialGroundView(self.arenaPath)

    def getDefaultName(self):
        return "New Floor"

    def getWidgets(self, container):
        self.listWidget = container.GroundList
        self.addButton = container.GroundAdd
        self.removeButton = container.GroundRemove
