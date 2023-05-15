import json

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from os.path import basename

from src.mission import MissionController
from src.util import ResourceLoader, displayError
from src.argosGenerator import generateArgosFile


class MainWindow(QMainWindow):  # TODO : Controller/View?
    def __init__(self):
        super().__init__()

        self.currentSavePath = None
        self.mission_controller = MissionController()

        ResourceLoader.loadWidget("MainWindow", self)
        self.setWindowTitle("Robot Skill Wizard")
        self.connectActions()

    def connectActions(self):
        self.actionNewMission.triggered.connect(self.onCreateMission)
        self.actionOpenMission.triggered.connect(self.onOpenMission)
        self.actionSave.triggered.connect(self.onSave)
        self.actionSave_as.triggered.connect(self.onSaveAs)
        self.actionGenerateArgosFile.triggered.connect(self.onGenerateArgos)

    def onCreateMission(self):
        self.mission_controller.createMission()
        self.setCentralWidget(self.mission_controller.getView())

    def onOpenMission(self):
        file_dialog = QFileDialog()
        # file_dialog.setNameFilter("(*.json)")
        file_path = file_dialog.getOpenFileName(None, "Open Mission", "", "Mission files (*.*)")[0]

        if file_path:
            with open(file_path, 'r') as mission_file:
                try:
                    mission_data = json.load(mission_file)
                    self.mission_controller.createMission(mission_data)
                    self.currentSavePath = file_path
                    self.setCentralWidget(self.mission_controller.getView())
                except json.JSONDecodeError:
                    displayError("Invalid Mission File", "The mission could not be loaded properly.")

    def onSave(self):
        if not self.mission_controller.hasCurrentMission():
            return

        if self.currentSavePath is None:
            self.onSaveAs()
        else:
            self.saveMission(self.currentSavePath)

    def onSaveAs(self):
        if not self.mission_controller.hasCurrentMission():
            return

        file_dialog = QFileDialog()
        file_path = file_dialog.getSaveFileName(None, "Save Mission", "", "Mission files (*.json)")[0]

        if file_path:
            self.saveMission(file_path)
            self.currentSavePath = file_path

    def saveMission(self, path):
        with open(path, 'w') as mission_file:
            json.dump(self.mission_controller.getMissionData(), mission_file, indent=2)

    def openMissionView(self):
        self.setCentralWidget(self.mission_controller.getView())

    def onGenerateArgos(self):
        if not self.mission_controller.hasCurrentMission():
            return

        file_dialog = QFileDialog()
        file_path = file_dialog.getSaveFileName(None, "Export to Argos", "", "Argos files (*.argos)")[0]

        if file_path:
            options = {}
            if self.currentSavePath:
                options["source"] = basename(self.currentSavePath)

            generateArgosFile(self.mission_controller.current_mission, file_path, **options)

