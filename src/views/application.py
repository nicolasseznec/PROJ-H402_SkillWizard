from PyQt5.QtWidgets import QMainWindow
from src.util import ResourceLoader
from src.views.mission import MissionView


class ApplicationViewListener:
    def onCreateMission(self):
        pass

    def onOpenMission(self):
        pass

    def onSave(self):
        pass

    def onSaveAs(self):
        pass

    # -------------------------

    def onGenerateArgos(self):
        pass

    def onGenerateFunctions(self):
        pass

    # -------------------------

    def onEditArena(self):
        pass

    def onEditObjective(self):
        pass


class ApplicationView(QMainWindow):
    """
    Main Window View

    Relays the user actions (from the action bar) to its controller
    """
    def __init__(self, *args):
        super().__init__(*args)
        ResourceLoader.loadWidget("MainWindow", self)
        self.setWindowTitle("Robot Skill Wizard")
        self.missionView = MissionView()

    def connectActions(self, listener: ApplicationViewListener):
        """
        Connects its actions to the given listener.
        """
        self.actionNewMission.triggered.connect(listener.onCreateMission)
        self.actionOpenMission.triggered.connect(listener.onOpenMission)
        self.actionSave.triggered.connect(listener.onSave)
        self.actionSaveAs.triggered.connect(listener.onSaveAs)
        self.actionGenerateArgosFile.triggered.connect(listener.onGenerateArgos)
        self.actionGenerateLoopFunctions.triggered.connect(listener.onGenerateFunctions)
        self.actionEditArena.triggered.connect(listener.onEditArena)
        self.actionEditObjective.triggered.connect(listener.onEditObjective)

    def displayMissionView(self):
        """
        Displays the mission editor.
        """
        self.setCentralWidget(self.missionView)

    def getMissionView(self):
        return self.missionView
