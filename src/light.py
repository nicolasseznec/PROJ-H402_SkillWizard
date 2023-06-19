from enum import Enum

from PyQt5.QtGui import QPen, QBrush, QPainterPath, QRadialGradient, QTransform, QLinearGradient
from PyQt5.QtCore import Qt, QPoint

from src.arenaObjects import MultiArenaZone, ArenaList, MultiArenaZoneModel, ArenaZone
from src.util import Color

LightColor = [Color.Red, Color.Green, Color.Blue, Color.Cyan, Color.Magenta, Color.Yellow]


class LightType(Enum):
    PointLight = 0
    WallLight = 1


LightTypes = [LightType.PointLight, LightType.WallLight]


class Light(MultiArenaZoneModel):
    def getAttributes(self):
        attributes = super(Light, self).getAttributes()
        attributes.update({
            "color": Color.Red.name,
            "lightType": LightType.PointLight.name,
            "strength": 10,
        })
        return attributes

    @classmethod
    def dummyLight(cls):
        return Light({
            "strength": 0,
        })


class LightView(MultiArenaZone):
    def __init__(self, arenaPath, *__args):
        self.strength = 10
        self.lightType = LightType.PointLight
        self.name = "New Light"
        self.color = Color.Red
        self.typePaths = {}

        super().__init__(arenaPath, *__args)

        self.setZValue(1)
        pen = QPen(Qt.NoPen)
        self.setPen(pen)
        self.updateColor()
        self.setType(self.lightType)
        self.updateDimensions()

    def paint(self, painter, option, widget=None):
        self.setPath(self.typePaths[self.lightType])

        if self.scenePos() != self.prev_pos:
            self.prev_pos = self.scenePos()
            self.updatePos()

        super(ArenaZone, self).paint(painter, option, widget)

    def connectSettings(self, container):
        if container is None:
            return
        self.settingsContainer = container
        container.LightType.currentIndexChanged.connect(self.typeChanged)
        container.LightColor.currentIndexChanged.connect(self.colorChanged)
        container.LightReset.clicked.connect(self.resetPosition)

        container.LightStrength.valueChanged.connect(self.strengthChanged)
        container.LightWidth.valueChanged.connect(self.widthChanged)
        container.LightOrientation.valueChanged.connect(self.orientationChanged)

        container.LightX.valueChanged.connect(self.posXChanged)
        container.LightY.valueChanged.connect(self.posYChanged)

    def disconnectSettings(self):
        if self.settingsContainer is None:
            return

        self.settingsContainer.LightType.currentIndexChanged.disconnect(self.typeChanged)
        self.settingsContainer.LightColor.currentIndexChanged.disconnect(self.colorChanged)
        self.settingsContainer.LightReset.clicked.disconnect(self.resetPosition)

        self.settingsContainer.LightStrength.valueChanged.disconnect(self.strengthChanged)
        self.settingsContainer.LightWidth.valueChanged.disconnect(self.widthChanged)
        self.settingsContainer.LightOrientation.valueChanged.disconnect(self.orientationChanged)

        self.settingsContainer.LightX.valueChanged.disconnect(self.posXChanged)
        self.settingsContainer.LightY.valueChanged.disconnect(self.posYChanged)

    def colorChanged(self, index):
        if self.blockSignal:
            return
        self.color = LightColor[index]

        self.updateColor()
        self.scene().update()
        self.onItemChanged(self.packChanges())

    def strengthChanged(self, value):
        if self.blockSignal:
            return
        self.strength = value
        self.updateDimensions()
        self.onItemChanged(self.packChanges())

    def setType(self, newtype):
        self.lightType = newtype
        self.updateColor()

    def typeChanged(self, index):
        if self.blockSignal:
            return
        self.setType(LightTypes[index])
        self.scene().update()
        self.onItemChanged(self.packChanges())

    def updateColor(self):
        color = Qt.white
        if self.color == Color.Red:
            color = Qt.red
        elif self.color == Color.Green:
            color = Qt.green
        elif self.color == Color.Blue:
            color = Qt.blue
        elif self.color == Color.Cyan:
            color = Qt.cyan
        elif self.color == Color.Magenta:
            color = Qt.magenta
        elif self.color == Color.Yellow:
            color = Qt.yellow

        if self.lightType == LightType.PointLight:
            gradient = QRadialGradient(QPoint(0, 0), self.radius)
        else:
            rotation = QTransform()
            rotation.rotate(self.orientation)
            gradient = QLinearGradient(QPoint(0, 0), rotation.map(QPoint(0, self.height)))

        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(0.08, Qt.white)
        gradient.setColorAt(0.3, color)
        gradient.setColorAt(1, Qt.transparent)

        self.setBrush(QBrush(gradient))

    def getTypePath(self, lightType):
        path = QPainterPath()

        if lightType == LightType.PointLight:
            self.radius = int(self.strength * 5)
            path.addEllipse(-self.radius, -self.radius, self.radius*2, self.radius*2)
        elif lightType == LightType.WallLight:
            self.height = int(self.strength * 3)
            path.addRect(-self.width/2, 0, self.width, self.height)
            rotation = QTransform()
            rotation.rotate(self.orientation)
            path = rotation.map(path)
        self.updateColor()
        return path

    def updateDimensions(self, shape=None, lightType=None):
        if lightType is not None:
            if lightType in LightTypes:
                self.typePaths[lightType] = self.getTypePath(lightType)
        else:
            self.typePaths = {s: self.getTypePath(s) for s in LightType}

        super(LightView, self).updateDimensions(shape)

    def updateProperties(self, model):
        self.lightType = LightType[model.lightType]
        self.color = Color[model.color]
        self.strength = model.strength
        super(LightView, self).updateProperties(model)
        self.updateView()

    def updateView(self):
        if self.settingsContainer is None:
            return
        self.blockSignal = True
        self.settingsContainer.LightWidth.setValue(self.width)
        self.settingsContainer.LightOrientation.setValue(self.orientation)
        self.settingsContainer.LightType.setCurrentIndex(LightTypes.index(self.lightType))
        self.settingsContainer.LightColor.setCurrentIndex(LightColor.index(self.color))
        self.settingsContainer.LightStrength.setValue(self.strength)
        self.updatePos()
        self.updateColor()
        self.blockSignal = False

    def updatePos(self):
        super(LightView, self).updatePos()
        self.settingsContainer.LightX.setValue(int(self.x()))
        self.settingsContainer.LightY.setValue(int(self.y()))

    def packChanges(self):
        changes = super(LightView, self).packChanges()
        changes.update({
            "color": self.color.name,
            "lightType": self.lightType.name,
            "strength": self.strength
        })
        return changes


class LightList(ArenaList):
    def itemFactory(self, arenaPath, model=None):
        return LightView(arenaPath, model)

    def getDefaultName(self):
        return "New Light"

    def getWidgets(self, container):
        self.listWidget = container.LightList
        self.addButton = container.LightAdd
        self.removeButton = container.LightRemove

    def packChanges(self):
        return {
            "lights": [item.packChanges() for item in self.items]
        }
