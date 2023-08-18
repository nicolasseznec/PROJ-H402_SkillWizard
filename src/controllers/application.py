import json
from os.path import basename

from lark import LarkError

from src.models.argos import generateArgosFile
from src.controllers.mission import MissionController
from src.models.objectiveUtils.loopFunctions import generateLoopFunctions

from src.views.application import ApplicationView, ApplicationViewListener
from src.util import getOpenFileName, getSaveFileName, displayError, displayInformation  # TODO : utils in MVC


class ApplicationController(ApplicationViewListener):
    def __init__(self, view: ApplicationView):
        self.currentSavePath = None
        self.view = view
        self.view.connectActions(self)

        self.missionController = MissionController(self.view.getMissionView())
        self.missionController.setFunctionGenerator(self.onGenerateFunctions)

    # ----------- Events --------------

    def onCreateMission(self):
        self.missionController.createMission()
        self.openMissionView()
        self.currentSavePath = None

    def onOpenMission(self):
        filePath = getOpenFileName("Open Mission", "Mission files (*.*)")

        if filePath:
            with open(filePath, 'r') as missionFile:
                try:
                    missionData = json.load(missionFile)
                    self.missionController.createMission(missionData)
                    self.openMissionView()
                    self.currentSavePath = filePath
                except json.JSONDecodeError:
                    displayError("Invalid Mission File", "The mission could not be loaded properly.")

    def onSave(self):
        if not self.canSave():
            return

        if self.currentSavePath is None:
            self.onSaveAs()
        else:
            self.saveMission(self.currentSavePath)

    def onSaveAs(self):
        if not self.canSave():
            return

        filePath = getSaveFileName("Save Mission", "Mission files (*.json)")

        if filePath:
            self.saveMission(filePath)
            self.currentSavePath = filePath

    def saveMission(self, path):
        with open(path, 'w') as mission_file:
            json.dump(self.missionController.getMissionData(), mission_file, indent=2)

    def canSave(self):
        return self.missionController.hasCurrentMission()

    def openMissionView(self):
        self.view.displayMissionView()

    # -------------------------

    def onGenerateArgos(self):
        if not self.missionController.hasCurrentMission():
            return

        filePath = getSaveFileName("Export to Argos", "Argos files (*.argos)")

        if filePath:
            options = {}
            if self.currentSavePath:
                options["source"] = basename(self.currentSavePath)

            generateArgosFile(self.missionController.currentMission, filePath, **options)

            displayInformation("Argos File Generation",
                               "The generated file still needs to be completed by the user at places indicated by 'TO COMPLETE'")

    def onGenerateFunctions(self):
        if not self.missionController.hasCurrentMission():
            return

        filePath = getSaveFileName("Generate C++ file", "C++ files (*.cpp)")

        if filePath:
            options = {}
            if self.currentSavePath:
                options["source"] = basename(self.currentSavePath)

            try:
                generateLoopFunctions(self.missionController.currentMission, filePath, **options)
                displayInformation("Loop Functions File Generation",
                                   "TODO")
            except LarkError:
                displayError("Generation Error", "Failed to generate the loop functions files due to a parsing error. One of the stages is not valid.")




    # -------------------------

    def onEditArena(self):
        if not self.missionController.hasCurrentMission():
            return
        self.missionController.selectArena()

    def onEditObjective(self):
        if not self.missionController.hasCurrentMission():
            return
        self.missionController.selectObjective()

    def show(self):
        self.view.show()
