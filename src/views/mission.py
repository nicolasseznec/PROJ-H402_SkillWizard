from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
from src.util import ResourceLoader
from src.views.robot import RobotModelView


class MissionView(QWidget):
    """
    UI for a mission
    """
    def __init__(self):
        super(MissionView, self).__init__()

        ResourceLoader.loadWidget("MissionView.ui", self)
        self.skillLayout: QVBoxLayout = self.SkillBoxContents.layout()
        self.skillLayout.setAlignment(Qt.AlignTop)

        self.behaviourLayout: QVBoxLayout = self.BehaviourBoxContents.layout()  # TODO : rename behavior in qtdesigner
        self.behaviourLayout.setAlignment(Qt.AlignTop)

        self.robotModelView = RobotModelView()

        self.view.addSettingsTab("Arena")
        self.view.addSettingsTab("Mission")
        self.view.addSettingsTab("Model", self.robotModelView)

        self.skillViews = {}  # skill views mapped to the id of their skill
        self.behaviorViews = {}  # behavior views mapped to the id of their behavior

    def addSkill(self, skill, view):
        self.skillViews[skill.id] = view
        self.skillLayout.addWidget(view.getSideWidget())
        self.registerToCenterPanel(view.getCenterWidget())

    def addBehaviour(self, behavior, view):
        self.behaviorViews[behavior.id] = view
        self.behaviourLayout.addWidget(view.getSideWidget())
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
