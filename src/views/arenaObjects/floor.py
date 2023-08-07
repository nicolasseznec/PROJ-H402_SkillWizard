from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt

from src.models.arenaObjects.floor import FloorColor
from src.util import Color
from src.views.arenaObjects.base import MultiArenaObjectView, ArenaListView


class FloorView(MultiArenaObjectView):
    def __init__(self, settingsContainer, *__args):
        super().__init__(settingsContainer, *__args)
        self.setBrush(QBrush(Qt.black))
        pen = QPen(Qt.NoPen)
        self.setPen(pen)

    def connectSettings(self, container):
        super(FloorView, self).connectSettings(container)
        self.colorSetting.currentIndexChanged.connect(self.colorChanged)

    def disconnectSettings(self):
        super(FloorView, self).disconnectSettings()
        self.colorSetting.currentIndexChanged.disconnect(self.colorChanged)

    def setupSettings(self, container):
        self.shapeSetting = container.GroundShape
        self.resetSetting = container.GroundReset
        self.colorSetting = container.GroundColor

        self.radiusSetting = container.GroundRadius
        self.orientationSetting = container.GroundOrientation
        self.widthSetting = container.GroundWidth
        self.heightSetting = container.GroundHeight

        self.xSetting = container.GroundX
        self.ySetting = container.GroundY

    def updateView(self, model):
        self.blockSignal = True
        color = Color[model.color]
        self.updateColor(color)
        self.colorSetting.setCurrentIndex(FloorColor.index(color))
        super(FloorView, self).updateView(model)

    def updateColor(self, color):
        if color == Color.Black:
            self.setBrush(QBrush(Qt.black))
        elif color == Color.White:
            self.setBrush(QBrush(Qt.white))
        elif color == Color.Gray:
            self.setBrush(QBrush(Qt.gray))

    # ---------- Events ------------

    def colorChanged(self, index):
        if self.blockSignal:
            return
        color = FloorColor[index]
        self.updateColor(color)
        self.scene().update()
        self.onItemChanged(color=color.name)


class FloorListView(ArenaListView):
    def createNewItem(self):
        return FloorView(self.settingsContainer)

    def getWidgets(self, settingsContainer):
        return settingsContainer.GroundAdd, settingsContainer.GroundRemove, settingsContainer.GroundList
