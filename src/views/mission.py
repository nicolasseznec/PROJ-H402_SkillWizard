from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
from src.util import ResourceLoader
from src.views.arena import ArenaView
from src.views.robot import RobotModelView


class MissionView(QWidget):
    """
    UI for a mission
    """
    def __init__(self, *args):
        super(MissionView, self).__init__(*args)

        ResourceLoader.loadWidget("MissionView.ui", self)
        self.skillLayout: QVBoxLayout = self.SkillBoxContents.layout()
        self.skillLayout.setAlignment(Qt.AlignTop)

        self.behaviorLayout: QVBoxLayout = self.BehaviorBoxContents.layout()
        self.behaviorLayout.setAlignment(Qt.AlignTop)

        self.robotModelView = RobotModelView()
        self.arenaView = ArenaView()
        self.registerToCenterPanel(self.arenaView.getCenterWidget())

        self.addSettingsTab("Arena", self.arenaView.settingsTab)
        self.addSettingsTab("Mission")
        self.addSettingsTab("Model", self.robotModelView)

        self.skillViews = {}  # skill views mapped to the id of their skill
        self.behaviorViews = {}  # behavior views mapped to the id of their behavior

    def addSkill(self, skill, view):
        self.skillViews[skill.id] = view
        self.skillLayout.addWidget(view.getSideWidget())
        self.registerToCenterPanel(view.getCenterWidget())

    def addBehavior(self, behavior, view):
        self.behaviorViews[behavior.id] = view
        self.behaviorLayout.addWidget(view.getSideWidget())
        self.registerToCenterPanel(view.getCenterWidget())

    def setCenterPanel(self, view):
        self.CenterPanel.setCurrentWidget(view)

    def registerToCenterPanel(self, view):
        self.CenterPanel.addWidget(view)

    def addSettingsTab(self, name, view=None):
        self.SettingsTabs.addTab(view if view is not None else QWidget(), name)

    def clearBehaviorsHighlight(self):
        for view in self.behaviorViews.values():
            view.setHighlighted(False)

    def highlightBehaviors(self, behaviorsIdList):
        for item in behaviorsIdList:
            self.behaviorViews[item].setHighlighted(True)
