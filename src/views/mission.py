from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
from src.util import ResourceLoader
from src.views.arena import ArenaView
from src.views.objective import ObjectiveView
from src.views.robot import RobotModelView


class MissionView(QWidget):
    """
    Base User Interface for a mission

    Handles the side panel and main panel.
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
        self.objectiveView = ObjectiveView()
        self.registerToCenterPanel(self.objectiveView.getCenterWidget())

        self.addSettingsTab("Arena", self.arenaView.settingsTab)
        self.addSettingsTab("Objective", self.objectiveView.settingsTab)
        self.addSettingsTab("Model", self.robotModelView)

        self.skillViews = {}  # skill views mapped to the id of their skill
        self.behaviorViews = {}  # behavior views mapped to the id of their behavior

    def addSkill(self, skill, view):
        """
        Adds a skill view to the available skills in the side panel. Also register the skill inspector (main panel)
        so it can be displayed when the skill is selected.
        """
        self.skillViews[skill.id] = view
        self.skillLayout.addWidget(view.getSideWidget())
        self.registerToCenterPanel(view.getCenterWidget())

    def addBehavior(self, behavior, view):
        """
        Adds a behavior view to the available behaviors in the side panel. Also register the skill inspector (main panel)
        so it can be displayed when the behavior is selected.
        """
        self.behaviorViews[behavior.id] = view
        self.behaviorLayout.addWidget(view.getSideWidget())
        self.registerToCenterPanel(view.getCenterWidget())

    def setCenterPanel(self, view):
        """
        Sets the main panel to the given view. The view must have been registered with registerToCenterPanel prior to
        calling this function.
        """
        self.CenterPanel.setCurrentWidget(view)

    def registerToCenterPanel(self, view):
        """
        Registers a view as a possible main panel so it can be selected later.
        """
        self.CenterPanel.addWidget(view)

    def addSettingsTab(self, name, view=None):
        """
        Adds a new tab to the settings tab.
        """
        self.SettingsTabs.addTab(view if view is not None else QWidget(), name)

    def setSettingsTab(self, index):
        """
        Set the current settings tab to the given index.
        """
        self.SettingsTabs.setCurrentIndex(index)

    def clearBehaviorsHighlight(self):
        """
        Remove all highlighting of behaviors. See highlightBehaviors.
        """
        for view in self.behaviorViews.values():
            view.setHighlighted(False)

    def highlightBehaviors(self, behaviorsIdList):
        """
        Highlights all behaviors from the given list in the side panel. This is used to display to which skill they are
        linked.
        """
        for item in behaviorsIdList:
            self.behaviorViews[item].setHighlighted(True)
