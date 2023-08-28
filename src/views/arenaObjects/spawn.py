from PyQt5.QtWidgets import QGraphicsItem

from src.views.arenaObjects.base import BaseArenaObjectView


class SpawnView(BaseArenaObjectView):
    """
    View for the spawn area object
    """
    def __init__(self, settingsContainer, *__args):
        super().__init__(settingsContainer, *__args)
        self.setZValue(2)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.blockSignal = False

    def setTabFocus(self, focus):
        self.setOpacity(0.7 if focus else 0.3)
        if focus:
            self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def setupSettings(self, container):
        self.shapeSetting = container.SpawnShape
        self.resetSetting = container.SpawnReset

        self.radiusSetting = container.SpawnRadius
        self.orientationSetting = container.SpawnOrientation
        self.widthSetting = container.SpawnWidth
        self.heightSetting = container.SpawnHeight

        self.xSetting = container.SpawnX
        self.ySetting = container.SpawnY
