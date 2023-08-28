from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt

from src.models.arenaObjects.floor import FloorColor
from src.util import Color
from src.views.arenaObjects.base import MultiArenaObjectView, ArenaListView


class FloorView(MultiArenaObjectView):
    """
    View for a floor object
    """
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
        self.shapeSetting = container.FloorShape
        self.resetSetting = container.FloorReset
        self.colorSetting = container.FloorColor

        self.radiusSetting = container.FloorRadius
        self.orientationSetting = container.FloorOrientation
        self.widthSetting = container.FloorWidth
        self.heightSetting = container.FloorHeight

        self.xSetting = container.FloorX
        self.ySetting = container.FloorY

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
        return settingsContainer.FloorAdd, settingsContainer.FloorRemove, settingsContainer.FloorList
