from PyQt5.QtGui import QPen, QBrush, QPainterPath, QRadialGradient, QTransform, QLinearGradient
from PyQt5.QtCore import Qt, QPoint

from src.models.arenaObjects.light import LightColor, LightTypes, LightType
from src.util import Color
from src.views.arenaObjects.base import ArenaListView, MultiArenaObjectView, BaseArenaObjectView


class LightView(MultiArenaObjectView):
    def __init__(self, settingsContainer, *__args):
        super().__init__(settingsContainer, *__args)
        self.setZValue(1)
        pen = QPen(Qt.NoPen)
        self.setPen(pen)

        self.lightType = LightType.PointLight
        self.typePaths = {}
        self.gradients = {}

    def paint(self, painter, option, widget=None):
        if self.lightType in self.typePaths:
            self.setPath(self.typePaths[self.lightType])

        if self.scenePos() != self.prev_pos:
            self.prev_pos = self.scenePos()
            self.updatePos()

        super(BaseArenaObjectView, self).paint(painter, option, widget)

    @staticmethod
    def getTypePath(lightType, **dimensions):
        path = QPainterPath()
        strength = dimensions.get("strength", 10)
        orientation = dimensions.get("orientation", 0)
        width = dimensions.get("width", 100)

        if lightType == LightType.PointLight:
            radius = int(strength * 5)
            path.addEllipse(-radius, -radius, radius*2, radius*2)
        elif lightType == LightType.WallLight:
            height = int(strength * 3)
            path.addRect(-width/2, 0, width, height)
            rotation = QTransform()
            rotation.rotate(orientation)
            path = rotation.map(path)
        return path

    def updateLights(self, lightType_=None, **dimensions):
        if lightType_ is not None:
            if lightType_ in LightTypes:
                self.typePaths[lightType_] = self.getTypePath(lightType_, **dimensions)
        else:
            self.typePaths = {s: self.getTypePath(s, **dimensions) for s in LightType}

    def setType(self, newtype):
        self.lightType = newtype
        if self.lightType in self.gradients:
            self.setBrush(QBrush(self.gradients[self.lightType]))

    def updateColor(self, newColor):
        if newColor == Color.Red:
            color = Qt.red
        elif newColor == Color.Green:
            color = Qt.green
        elif newColor == Color.Blue:
            color = Qt.blue
        elif newColor == Color.Cyan:
            color = Qt.cyan
        elif newColor == Color.Magenta:
            color = Qt.magenta
        elif newColor == Color.Yellow:
            color = Qt.yellow
        else:
            color = Qt.white

        # TODO : use dimensions
        self.gradients[LightType.PointLight] = QRadialGradient(QPoint(0, 0), 50)
        rotation = QTransform()
        rotation.rotate(0)
        self.gradients[LightType.WallLight] = QLinearGradient(QPoint(0, 0), rotation.map(QPoint(0, 50)))

        for gradient in self.gradients.values():
            gradient.setColorAt(0, Qt.white)
            gradient.setColorAt(0.08, Qt.white)
            gradient.setColorAt(0.3, color)
            gradient.setColorAt(1, Qt.transparent)

        self.setBrush(QBrush(self.gradients[self.lightType]))

    def updateView(self, model):
        self.blockSignal = True
        color = Color[model.color]
        self.updateColor(color)
        self.setType(LightType[model.lightType])
        self.setPos(model.x, model.y)
        self.updatePos()
        self.updateLights(
            strength=model.strength,
            orientation=model.orientation,
            width=model.width,
        )

        self.colorSetting.setCurrentIndex(LightColor.index(color))
        self.typeSetting.setCurrentIndex(LightTypes.index(self.lightType))
        self.orientationSetting.setValue(model.orientation)
        self.widthSetting.setValue(model.width)
        self.blockSignal = False

    # ---------- Connecting the view ------------

    def connectSettings(self, container):
        self.setupSettings(container)

        self.resetSetting.clicked.connect(self.onResetPosition)
        self.colorSetting.currentIndexChanged.connect(self.colorChanged)
        self.typeSetting.currentIndexChanged.connect(self.typeChanged)

        self.strengthSetting.valueChanged.connect(self.strengthChanged)
        self.widthSetting.valueChanged.connect(self.widthChanged)
        self.orientationSetting.valueChanged.connect(self.orientationChanged)

        self.xSetting.valueChanged.connect(self.posXChanged)
        self.ySetting.valueChanged.connect(self.posYChanged)

    def disconnectSettings(self):
        self.resetSetting.clicked.disconnect(self.onResetPosition)
        self.colorSetting.currentIndexChanged.disconnect(self.colorChanged)
        self.typeSetting.currentIndexChanged.disconnect(self.typeChanged)

        self.strengthSetting.valueChanged.disconnect(self.strengthChanged)
        self.widthSetting.valueChanged.disconnect(self.widthChanged)
        self.orientationSetting.valueChanged.disconnect(self.orientationChanged)

        self.xSetting.valueChanged.disconnect(self.posXChanged)
        self.ySetting.valueChanged.disconnect(self.posYChanged)

    def setupSettings(self, container):
        self.resetSetting = container.LightReset
        self.colorSetting = container.LightColor
        self.typeSetting = container.LightType

        self.strengthSetting = container.LightStrength
        self.widthSetting = container.LightWidth
        self.orientationSetting = container.LightOrientation

        self.xSetting = container.LightX
        self.ySetting = container.LightY

    # ---------- Events ------------

    def colorChanged(self, index):
        if self.blockSignal:
            return
        color = LightColor[index]
        self.updateColor(color)
        self.scene().update()
        self.onItemChanged(color=color.name)

    def strengthChanged(self, value):
        if self.blockSignal:
            return
        self.onItemChanged(strength=value)

    def typeChanged(self, index):
        if self.blockSignal:
            return
        self.setType(LightTypes[index])
        self.scene().update()
        self.onItemChanged(lightType=self.lightType.name)


class LightListView(ArenaListView):
    def createNewItem(self):
        return LightView(self.settingsContainer)

    def getWidgets(self, settingsContainer):
        return settingsContainer.LightAdd, settingsContainer.LightRemove, settingsContainer.LightList
