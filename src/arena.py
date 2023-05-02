from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

from src.util import ResourceLoader, Event


class ArenaView(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ArenaInspector.ui", self)

        self.settingsTab = ResourceLoader.loadWidget("ArenaSettingsTab.ui")
        self.settingsTab.layout().setAlignment(Qt.AlignTop)

        self.settingsTab.ArenaEditButton.clicked.connect(self.ArenaClicked)
        self.onArenaClicked = Event()

    def getCenterWidget(self):
        return self

    def paintEvent(self, event):
        super(ArenaView, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawRect(50, 50, 100, 50)
        painter.setBrush(QColor(0, 255, 0))
        painter.drawEllipse(150, 75, 50, 50)

    def ArenaClicked(self):
        self.onArenaClicked()


class ArenaController:
    def __init__(self):
        self.view = ArenaView()
        self.onArenaSelected = Event()

        self.view.onArenaClicked += self.onArenaClicked

    def getView(self):
        return self.view

    def getTab(self):
        return self.view.settingsTab

    def setSelected(self, selected):
        pass

    def onArenaClicked(self):
        self.onArenaSelected(self)
