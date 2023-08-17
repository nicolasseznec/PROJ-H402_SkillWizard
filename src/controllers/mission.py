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
    Controller for the current opened mission
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
        self.resetModel()  # TODO : check if there already is a mission open
        self.setCurrentMission(Mission(self.skills, self.behaviors, self.robotModelController.models, data))

    def setCurrentMission(self, mission):
        self.currentMission = mission
        self.updateSkills()
        self.updateBehaviors()
        self.updateRobotModel(mission.referenceModel.reference)
        self.updateArena()
        self.updateObjective()

    def getMissionData(self):
        if self.currentMission is None:
            return {}
        return self.currentMission.toJson()

    def getView(self):
        return self.view

    def hasCurrentMission(self):
        return self.currentMission is not None

    def selectArena(self):
        self.onItemSelected(self.arenaController)
        self.view.setSettingsTab(0)

    def selectObjective(self):
        self.onItemSelected(self.objectiveController)
        self.view.setSettingsTab(1)

    def setFunctionGenerator(self, functionGenerator):
        self.objectiveController.setFunctionGenerator(functionGenerator)

    # ------------ Updating ---------------

    def updateSkills(self):
        for controller in self.skillControllers.values():
            controller.updateView()

    def updateBehaviors(self):
        for controller in self.behaviorControllers.values():
            controller.updateView()

    def updateRobotModel(self, reference):
        self.robotModelController.setModel(reference)
        if self.currentMission:
            self.currentMission.setModel(self.robotModelController.current)

    def updateArena(self):
        self.arenaController.setArena(self.currentMission.arena)

    def updateObjective(self):
        self.objectiveController.setObjective(self.currentMission.objective)

    # --------------- Loading the application model (skills and behaviors) ---------------

    def generateModel(self, modelPath):
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
        self.skillControllers[skill.id] = controller
        self.view.addSkill(skill, view)
        self.skills[skill.id] = skill

    def addBehavior(self, behavior, view, controller):
        self.behaviorControllers[behavior.id] = controller
        self.view.addBehavior(behavior, view)
        self.behaviors[behavior.id] = behavior
        for s_id in behavior.skills:
            self.skills[s_id].linkBehavior(behavior.id)

    def resetModel(self):
        for skillController in self.skillControllers.values():
            skillController.reset()
        for behaviorController in self.behaviorControllers.values():
            behaviorController.reset()

    # ---------------- Events -------------------------

    def onItemSelected(self, item):  # TODO : interface for item and itemView ?
        self.view.clearBehaviorsHighlight()

        if self.selectedItem is not None:
            self.selectedItem.setSelected(False)
        item.setSelected(True)
        self.selectedItem = item

        self.view.setCenterPanel(item.getCenterWidget())

    def onSkillSelected(self, skillController):
        self.onItemSelected(skillController)
        self.view.highlightBehaviors(skillController.getBehaviorsIds())

    def onSkillChecked(self, skill, checked):
        if checked:
            self.currentMission.enableSkill(skill)
        else:
            self.currentMission.disableSkill(skill)
