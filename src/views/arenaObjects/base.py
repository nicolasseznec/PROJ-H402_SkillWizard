from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QToolButton, QListWidget
from PyQt5.QtGui import QColor, QPainterPath, QPen, QBrush, QTransform
from PyQt5.QtCore import Qt, QPointF

from src.util import Event, Shape
from src.models.arenaObjects.base import ArenaObjectShape
from src.views.utils.itemList import ItemListView, TextDialog


class BaseArenaObjectView(QGraphicsPathItem):
    """
    View for a basic arena object.
    """
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
        """
        PyQt paint event of QGraphicsPathItem, called each time the item is drawn.
        """
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
        """
        Update the content of the view from the given model
        """
        block = self.blockSignal
        self.blockSignal = True
        self.setShape(Shape[model.shape])
        self.setPos(model.x, model.y)
        self.updatePos()
        self.updateShapes(
            radius=model.radius,
            orientation=model.orientation,
            width=model.width,
            height=model.height
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
        """
        Connect the settings signals to the view's own events.
        """
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
    def getShapePath(shape_, **dimensions):
        """
        Creates the QPainterPath of this item for a given shape.
        """
        width = dimensions.get("width", 100)
        height = dimensions.get("height", 100)
        radius = dimensions.get("radius", 50)
        orientation = dimensions.get("orientation", 0)

        path = QPainterPath()
        if shape_ == Shape.Rectangle:
            path.addRect(-width / 2, -height / 2, width, height)
            rotation = QTransform()
            rotation.rotate(orientation)
            path = rotation.map(path)
        elif shape_ == Shape.Circle:
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
        # self.setX(value)
        self.onItemChanged(x=value)

    def posYChanged(self, value):
        if self.blockSignal:
            return
        # self.setY(value)
        self.onItemChanged(y=value)

    def onResetPosition(self):
        if self.blockSignal:
            return
        pos = self.scene().center
        self.onItemChanged(x=pos.x(), y=pos.y())


class MultiArenaObjectView(BaseArenaObjectView):
    """
    View for an arena object that can be put in a list.
    """
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
        """
        Called from PyQt when any event occurs. Catch the selection event and relays it to a controller.
        """
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.onSelected()
            self.blockSignal = not value

        return super(MultiArenaObjectView, self).itemChange(change, value)


# ------------ Item Lists --------------

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
