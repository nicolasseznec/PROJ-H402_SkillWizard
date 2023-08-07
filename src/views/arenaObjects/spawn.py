from PyQt5.QtWidgets import QGraphicsItem

from src.views.arenaObjects.base import BaseArenaObjectView


class SpawnView(BaseArenaObjectView):
    def __init__(self, settingsContainer, *__args):
        super().__init__(settingsContainer, *__args)
        self.setZValue(2)

    def setTabFocus(self, focus):
        self.setOpacity(0.7 if focus else 0.3)
        if focus:
            self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def setupSettings(self, container):
        self.shapeSetting = container.StartAreaShape
        self.resetSetting = container.StartAreaReset

        self.radiusSetting = container.StartAreaRadius
        self.orientationSetting = container.StartAreaOrientation
        self.widthSetting = container.StartAreaWidth
        self.heightSetting = container.StartAreaHeight

        self.xSetting = container.StartAreaX
        self.ySetting = container.StartAreaY
