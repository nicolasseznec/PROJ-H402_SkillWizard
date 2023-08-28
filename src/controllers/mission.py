import json

from src.controllers.arena import ArenaController
from src.controllers.behavior import BehaviorLoader
from src.controllers.objective import ObjectiveController
from src.controllers.robot import RobotModelController, RobotModelLoader
from src.controllers.skill import SkillLoader
from src.models.mission import Mission
from src.util import ResourceLoader, displayError
from src.views.mission import MissionView


class MissionController:
    """
    Controller for the mission

    Contains all sub controllers for different parts of the mission
    """
    def __init__(self, view: MissionView):
        self.view = view
        self.currentMission = None
        self.selectedItem = None

        self.robotModelController = RobotModelController(self.view.robotModelView)
        self.robotModelController.modelChanged += self.updateRobotModel
        self.arenaController = ArenaController(self.view.arenaView)
        self.arenaController.onSelected += self.onItemSelected
        self.objectiveController = ObjectiveController(self.view.objectiveView)
        self.objectiveController.onSelected += self.onItemSelected

        self.skills = {}  # references for existing skills
        self.behaviors = {}  # references for existing behaviors

        self.skillControllers = {}  # skill controllers mapped to the id of their skill
        self.behaviorControllers = {}  # behavior controllers mapped to the id of their behavior
        self.generateModel("model.json")

    # --------- Called from Main Application Window -----------

    def createMission(self, data=None):
        """
        Creates a mission from the given data. The data is a dict following the same structure as a json mission file.
        If data is None or not given, creates a blank new mission.
        """
        self.resetModel()  # TODO : check if there already is a mission open
        self.setCurrentMission(Mission(self.skills, self.behaviors, self.robotModelController.models, data))

    def setCurrentMission(self, mission):
        """
        Sets the current mission and updates all controllers (and their views) accordingly
        """
        self.currentMission = mission
        self.updateSkills()
        self.updateBehaviors()
        self.updateRobotModel(mission.referenceModel.reference)
        self.updateArena()
        self.updateObjective()

    def getMissionData(self):
        """
        Returns the mission as a dict, directly convertible to a json file.
        """
        if self.currentMission is None:
            return {}
        return self.currentMission.toJson()

    def getView(self):
        return self.view

    def hasCurrentMission(self):
        """
        Whether the controller currently has a mission.
        """
        return self.currentMission is not None

    def selectArena(self):
        """
        Selects the arena editor in the main panel and in the settings tab.
        """
        self.onItemSelected(self.arenaController)
        self.view.setSettingsTab(0)

    def selectObjective(self):
        """
        Selects the objective editor in the main panel and in the settings tab.
        """
        self.onItemSelected(self.objectiveController)
        self.view.setSettingsTab(1)

    def setFunctionGenerator(self, functionGenerator):
        """
        Gives the objective functions generations method to the objective controller. This way it can directly generate
        the functions when the user clicks the corresponding button.
        """
        self.objectiveController.setFunctionGenerator(functionGenerator)

    # ------------ Updating ---------------

    def updateSkills(self):
        """
        Updates all skills to the new mission.
        """
        for controller in self.skillControllers.values():
            controller.updateView()

    def updateBehaviors(self):
        """
        Updates all behaviors to the new mission.
        """
        for controller in self.behaviorControllers.values():
            controller.updateView()

    def updateRobotModel(self, reference):
        """
        Updates the robot reference model to the new mission.
        """
        self.robotModelController.setModel(reference)
        if self.currentMission:
            self.currentMission.setModel(self.robotModelController.current)

    def updateArena(self):
        """
        Updates the arena editor to the new mission.
        """
        self.arenaController.setArena(self.currentMission.arena)

    def updateObjective(self):
        """
        Updates the objective editor to the new mission.
        """
        self.objectiveController.setObjective(self.currentMission.objective)

    # --------------- Loading the application model (skills and behaviors) ---------------

    def generateModel(self, modelPath):
        """
        Loads the model from the given path and create all the corresponding skills, behaviors, and robot reference models.
        """
        with ResourceLoader.openData(modelPath) as modelFile:
            try:
                modelData = json.load(modelFile)
                SkillLoader.loadSkills(modelData, self.addSkill, self.onSkillSelected, self.onSkillChecked)
                BehaviorLoader.loadBehaviors(modelData, self.addBehavior, self.onItemSelected)
                RobotModelLoader.loadModels(modelData, self.robotModelController)

            except json.JSONDecodeError:
                displayError("Invalid Model File", "The model could not be loaded properly.")
                raise

    def addSkill(self, skill, view, controller):
        """
        Adds a new skill to the available skills.
        """
        self.skillControllers[skill.id] = controller
        self.view.addSkill(skill, view)
        self.skills[skill.id] = skill

    def addBehavior(self, behavior, view, controller):
        """
        Adds a new behavior to the available behavior.
        """
        self.behaviorControllers[behavior.id] = controller
        self.view.addBehavior(behavior, view)
        self.behaviors[behavior.id] = behavior
        for s_id in behavior.skills:
            self.skills[s_id].linkBehavior(behavior.id)

    def resetModel(self):
        """
        Resests every skill and behavior as disabled.
        """
        for skillController in self.skillControllers.values():
            skillController.reset()
        for behaviorController in self.behaviorControllers.values():
            behaviorController.reset()

    # ---------------- Events -------------------------

    def onItemSelected(self, item):  # TODO : interface for item and itemView ?
        """
        Called when an item is selected in the side panel. It updates the current selected item and displays its inspector
        in the main panel.
        """
        self.view.clearBehaviorsHighlight()

        if self.selectedItem is not None:
            self.selectedItem.setSelected(False)
        item.setSelected(True)
        self.selectedItem = item

        self.view.setCenterPanel(item.getCenterWidget())

    def onSkillSelected(self, skillController):
        """
        Called when a skill is selected. Same as onItemSelected but also highlights the linked behaviors.
        """
        self.onItemSelected(skillController)
        self.view.highlightBehaviors(skillController.getBehaviorsIds())

    def onSkillChecked(self, skill, checked):
        """
        Called when a skill is enabled or disabled. Updates the behaviors in the mission accordingly.
        """
        if checked:
            self.currentMission.enableSkill(skill)
        else:
            self.currentMission.disableSkill(skill)
