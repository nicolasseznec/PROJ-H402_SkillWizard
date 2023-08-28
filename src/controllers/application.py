import json
from os.path import basename

from lark import LarkError

from src.models.argos import generateArgosFile
from src.controllers.mission import MissionController
from src.models.objectiveUtils.loopFunctions import generateLoopFunctions

from src.views.application import ApplicationView, ApplicationViewListener
from src.util import getOpenFileName, getSaveFileName, displayError, displayInformation  # TODO : utils in MVC


class ApplicationController(ApplicationViewListener):
    """
    Main application controller

    Handles the actions for file creation, loading and saving.
    """
    def __init__(self, view: ApplicationView):
        self.currentSavePath = None
        self.view = view
        self.view.connectActions(self)

        self.missionController = MissionController(self.view.getMissionView())
        self.missionController.setFunctionGenerator(self.onGenerateFunctions)

    # ----------- Events --------------

    def onCreateMission(self):
        """
        Called when the user creates a new file. Creates a blank mission.
        """
        self.missionController.createMission()
        self.openMissionView()
        self.currentSavePath = None

    def onOpenMission(self):
        """
        Called when the user laods a mission file. Loads the file data into a new mission.
        """
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
        """
        Called when the user saves the current mission. If it is not assiciated to a file yet, it calls onSaveAs instead.
        """
        if not self.canSave():
            return

        if self.currentSavePath is None:
            self.onSaveAs()
        else:
            self.saveMission(self.currentSavePath)

    def onSaveAs(self):
        """
        Called when the user wants to save the current mission to a specific file.
        """
        if not self.canSave():
            return

        filePath = getSaveFileName("Save Mission", "Mission files (*.json)")

        if filePath:
            self.saveMission(filePath)
            self.currentSavePath = filePath

    def saveMission(self, path):
        """
        Save the current mission to the specified path.
        """
        with open(path, 'w') as mission_file:
            json.dump(self.missionController.getMissionData(), mission_file, indent=2)

    def canSave(self):
        """
        Whether the current mission can be saved or not.
        """
        return self.missionController.hasCurrentMission()

    def openMissionView(self):
        """
        Called when a mission is opened or created, to display its interface.
        """
        self.view.displayMissionView()

    # -------------------------

    def onGenerateArgos(self):
        """
        Called when the user wants to generate the ARGoS file from the current mission.
        Opens a file browser and saves the generated code to the desired files.
        """
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
        """
        Called when the user wants to generate the Objective functions files from the current mission.
        Opens a file browser and saves the generated code to the desired files.
        """
        if not self.missionController.hasCurrentMission():
            return

        filePath = getSaveFileName("Generate C++ file", "C++ files (*.cpp)")

        if filePath:
            options = {}
            if self.currentSavePath:
                options["source"] = basename(self.currentSavePath)

            try:
                generateLoopFunctions(self.missionController.currentMission, filePath, **options)
                displayInformation("Loop Functions Generation",
                                   "Functions have been generated in a .h and .cpp file.")
            except (LarkError, KeyError):
                displayError("Generation Error", "Failed to generate the loop functions files due to a parsing error. One of the stages is not valid.")

    # -------------------------

    def onEditArena(self):
        """
        Called when the user clicks on the "Edit Arena" action.
        Selects the arena inspector in the main panel
        """
        if not self.missionController.hasCurrentMission():
            return
        self.missionController.selectArena()

    def onEditObjective(self):
        """
        Called when the user clicks on the "Edit Objective" action.
        Selects the objective inspector in the main panel
        """
        if not self.missionController.hasCurrentMission():
            return
        self.missionController.selectObjective()

    def show(self):
        """
        Displays the application window.
        """
        self.view.show()
