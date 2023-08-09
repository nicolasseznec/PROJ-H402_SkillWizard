from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QGraphicsPathItem, \
    QGraphicsItem, QToolButton, QListWidget
from PyQt5.QtGui import QColor, QPainterPath, QPen, QBrush, QTransform
from PyQt5.QtCore import Qt, QPointF

from src.util import Event, Shape
from src.models.arenaObjects.base import ArenaObjectShape


class BaseArenaObjectView(QGraphicsPathItem):
    def __init__(self, settingsContainer, *__args):
        super().__init__(*__args)

        self.setBrush(QBrush(QColor(224, 126, 134, 255)))
        pen = QPen(QColor(Qt.black))
        pen.setWidth(2)
        pen.setStyle(Qt.DashDotLine)
        self.setPen(pen)

        self.prev_pos = QPointF(0, 0)
        self.shape = None

        self.shapePaths = {}
        self.arenaPath = None
        self.settingsContainer = settingsContainer
        self.connectSettings(settingsContainer)
        self.onItemChanged = Event()
        self.blockSignal = True

    def paint(self, painter, option, widget=None):
        if self.arenaPath is not None and self.shape in self.shapePaths:
            intersect = self.arenaPath.intersected(self.shapePaths[self.shape].translated(self.scenePos())) \
                .translated(-self.scenePos())
            intersect.closeSubpath()
            self.setPath(intersect)

        if self.scenePos() != self.prev_pos:
            self.prev_pos = self.scenePos()
            self.updatePos()

        super(BaseArenaObjectView, self).paint(painter, option, widget)

    def updateView(self, model):
        block = self.blockSignal
        self.blockSignal = True
        self.setShape(Shape[model.shape])
        self.setPos(model.x, model.y)
        self.updatePos()
        self.updateShapes(
            radius=model.radius,
            orientation=model.orientation,
            width=model.width,
            heigth=model.height,
        )

        self.shapeSetting.setCurrentIndex(ArenaObjectShape.index(self.shape))
        self.radiusSetting.setValue(model.radius)
        self.orientationSetting.setValue(model.orientation)
        self.widthSetting.setValue(model.width)
        self.heightSetting.setValue(model.height)
        self.blockSignal = block

    def updatePos(self):
        self.xSetting.setValue(int(self.x()))
        self.ySetting.setValue(int(self.y()))

    def setArenaPath(self, arenaPath):
        self.arenaPath = arenaPath

    # ---------- Connecting the view ------------

    def setupSettings(self, container):
        pass

    def connectSettings(self, container):
        self.setupSettings(container)

        self.shapeSetting.currentIndexChanged.connect(self.shapeChanged)
        self.resetSetting.clicked.connect(self.onResetPosition)

        self.radiusSetting.valueChanged.connect(self.radiusChanged)
        self.orientationSetting.valueChanged.connect(self.orientationChanged)
        self.widthSetting.valueChanged.connect(self.widthChanged)
        self.heightSetting.valueChanged.connect(self.heightChanged)

        self.xSetting.valueChanged.connect(self.posXChanged)
        self.ySetting.valueChanged.connect(self.posYChanged)

    def disconnectSettings(self):
        self.shapeSetting.currentIndexChanged.disconnect(self.shapeChanged)
        self.resetSetting.clicked.disconnect(self.onResetPosition)

        self.radiusSetting.valueChanged.disconnect(self.radiusChanged)
        self.orientationSetting.valueChanged.disconnect(self.orientationChanged)
        self.widthSetting.valueChanged.disconnect(self.widthChanged)
        self.heightSetting.valueChanged.disconnect(self.heightChanged)

        self.xSetting.valueChanged.disconnect(self.posXChanged)
        self.ySetting.valueChanged.disconnect(self.posYChanged)

    # ---------- Shape paths management ------------

    def setShape(self, shape):
        self.shape = shape

    def updateShapes(self, shape_=None, **dimensions):
        if shape_ is not None:
            self.shapePaths[shape_] = self.getShapePath(shape_, **dimensions)
        else:
            self.shapePaths = {shape: self.getShapePath(shape, **dimensions) for shape in ArenaObjectShape}

        scene = self.scene()
        if scene is not None:
            scene.update()

    @staticmethod
    def getShapePath(shape, **dimensions):
        width = dimensions.get("width", 100)
        height = dimensions.get("height", 100)
        radius = dimensions.get("radius", 50)
        orientation = dimensions.get("orientation", 0)

        path = QPainterPath()
        if shape == Shape.Rectangle:
            path.addRect(-width / 2, -height / 2, width, height)
            rotation = QTransform()
            rotation.rotate(orientation)
            path = rotation.map(path)
        elif shape == Shape.Circle:
            path.addEllipse(-radius, -radius, radius * 2, radius * 2)

        return path

    # ---------- Events ------------

    def shapeChanged(self, index):
        if self.blockSignal:
            return
        self.setShape(ArenaObjectShape[index])
        self.scene().update()
        self.onItemChanged(shape=self.shape.name)

    def radiusChanged(self, value):
        if self.blockSignal:
            return
        self.onItemChanged(radius=value)

    def orientationChanged(self, value):
        if self.blockSignal:
            return
        self.onItemChanged(orientation=value)

    def widthChanged(self, value):
        if self.blockSignal:
            return
        self.onItemChanged(width=value)

    def heightChanged(self, value):
        if self.blockSignal:
            return
        self.onItemChanged(height=value)

    def posXChanged(self, value):
        if self.blockSignal:
            return
        self.setX(value)
        self.onItemChanged(x=value)

    def posYChanged(self, value):
        if self.blockSignal:
            return
        self.setY(value)
        self.onItemChanged(y=value)

    def onResetPosition(self):
        if self.blockSignal:
            return
        pos = self.scene().center
        self.onItemChanged(x=pos.x(), y=pos.y())


class MultiArenaObjectView(BaseArenaObjectView):
    def __init__(self, settingsContainer, *__args):
        super().__init__(settingsContainer, *__args)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.onSelected = Event()

    def setTabFocus(self, focus):
        if focus:
            self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.setSelected(False)

    # ---------- Events ------------

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.onSelected()
            self.blockSignal = not value

        return super(MultiArenaObjectView, self).itemChange(change, value)


# ------------ Item Lists --------------

class ItemListView:
    def __init__(self, addButton, removeButton, listWidget):
        self.items = []

        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemSelected = Event()
        self.onItemDoubleClicked = Event()

        self.listWidget = listWidget
        self.addButton = addButton
        self.removeButton = removeButton
        self.connectWidgets()

    def connectWidgets(self):
        self.listWidget.currentRowChanged.connect(self.onSelectedChanged)
        self.listWidget.itemDoubleClicked.connect(self.onDoubleClick)
        self.addButton.clicked.connect(self.onAdd)
        self.removeButton.clicked.connect(self.onRemove)

    def createNewItem(self):
        return None

    def getItem(self, index):
        return self.items[index]

    def getCurrentIndex(self):
        return self.listWidget.currentRow()

    def selectRow(self, index):
        self.listWidget.blockSignals(True)
        self.listWidget.setCurrentRow(index)
        self.listWidget.blockSignals(False)

    def setItemText(self, index, text):
        self.listWidget.item(index).setText(text)

    # ---------- Events ------------

    def onAdd(self):
        self.onItemAdded()

    def onRemove(self):
        index = self.listWidget.currentRow()
        if index < 0 or index >= len(self.items):
            return
        self.onItemRemoved(index)

    def onSelectedChanged(self, index):
        self.onItemSelected(index)

    def onDoubleClick(self, item):
        self.onItemDoubleClicked(self.listWidget.row(item))

    # ----------- Add/Remove -------------

    def addItem(self, item, name="New Item"):
        self.listWidget.addItem(name)
        self.items.append(item)

    def removeItem(self, index):
        self.listWidget.takeItem(index)
        self.items.pop(index)

    # -------------------------------------

    def clear(self):
        self.listWidget.blockSignals(True)
        self.listWidget.clear()
        self.listWidget.blockSignals(False)
        self.items.clear()


class TextDialog(QDialog):
    def __init__(self, parent=None, initialText='', dialogName=''):
        super().__init__(parent)
        if dialogName:
            self.setWindowTitle(dialogName)
        self.setLayout(QVBoxLayout())

        lineEdit = QLineEdit()
        if initialText:
            lineEdit.setText(initialText)
            lineEdit.selectAll()
        self.layout().addWidget(lineEdit)

        buttons_layout = QHBoxLayout()
        self.layout().addLayout(buttons_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def getLineEditValue(self):
        return self.layout().itemAt(0).widget().text()

    def getNewText(self):
        if self.exec_() == QDialog.Accepted:
            return self.getLineEditValue()


class ArenaListView(ItemListView):
    def __init__(self, settingsContainer):
        self.settingsContainer = settingsContainer
        addButton, removeButton, listWidget = self.getWidgets(settingsContainer)
        super().__init__(addButton, removeButton, listWidget)

    def getWidgets(self, settingsContainer):
        return QToolButton(), QToolButton(), QListWidget()

    def getTextDialog(self, index):
        item = self.listWidget.item(index)
        return TextDialog(self.listWidget, item.text(), "Change name")
