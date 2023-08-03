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

    def onGenerateArgos(self):
        pass


class ApplicationView(QMainWindow):
    def __init__(self):
        super().__init__()
        ResourceLoader.loadWidget("MainWindow", self)
        self.setWindowTitle("Robot Skill Wizard")

        self.missionView = MissionView()

    def connectActions(self, listener: ApplicationViewListener):
        self.actionNewMission.triggered.connect(listener.onCreateMission)
        self.actionOpenMission.triggered.connect(listener.onOpenMission)
        self.actionSave.triggered.connect(listener.onSave)
        self.actionSaveAs.triggered.connect(listener.onSaveAs)
        self.actionGenerateArgosFile.triggered.connect(listener.onGenerateArgos)

    def displayMissionView(self):
        self.setCentralWidget(self.missionView)

    def getMissionView(self):
        return self.missionView
