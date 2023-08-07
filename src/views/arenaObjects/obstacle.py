from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt

from src.views.arenaObjects.base import MultiArenaObjectView, ArenaListView


class ObstacleView(MultiArenaObjectView):
    def __init__(self, settingsContainer, *__args):
        super().__init__(settingsContainer, *__args)
        self.setZValue(2)

        brush = QBrush(Qt.black, Qt.Dense2Pattern)
        self.setBrush(brush)
        pen = QPen(Qt.gray)
        pen.setWidth(2)
        self.setPen(pen)

    def setupSettings(self, container):
        self.shapeSetting = container.ObstacleShape
        self.resetSetting = container.ObstacleReset

        self.radiusSetting = container.ObstacleRadius
        self.orientationSetting = container.ObstacleOrientation
        self.widthSetting = container.ObstacleWidth
        self.heightSetting = container.ObstacleHeight

        self.xSetting = container.ObstacleX
        self.ySetting = container.ObstacleY


class ObstacleListView(ArenaListView):
    def createNewItem(self):
        return ObstacleView(self.settingsContainer)

    def getWidgets(self, settingsContainer):
        return settingsContainer.ObstacleAdd, settingsContainer.ObstacleRemove, settingsContainer.ObstacleList

