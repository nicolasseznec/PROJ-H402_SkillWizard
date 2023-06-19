from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
import json

from src.model import RobotModelController
from src.util import ResourceLoader, displayError, Event
from src.skill import SkillController, SkillView, Skill
from src.behaviour import Behaviour, BehaviourController
from src.arena import ArenaController, Arena


class Mission:
    """
    Model for a mission (selected skills, behaviours, objective function and other parameters)
    """
    def __init__(self, data=None):
        self.selected_skills = []  # list of selected skills
        self.behaviours = []  # list of behaviours related to selected skills
        self.model_data = None
        self.reference_model = None

        if data is not None:
            self.loadFromData(data)
        else:
            self.arena = Arena()

    def toJson(self):
        return {
            "Skills": [s.toJson() for s in self.selected_skills if s.active],
            "Behaviours": [b.toJson() for b in self.behaviours if b.active],
            "Arena": self.arena.toJson(),
            "ReferenceModel": self.reference_model.toJson(),
        }

    def loadFromData(self, data):
        self.model_data = data
        self.arena = Arena(data["Arena"])

    def getSkillData(self):
        return {} if self.model_data is None else self.model_data["Skills"]

    def getBehaviourData(self):
        return {} if self.model_data is None else self.model_data["Behaviours"]

    def getArenaData(self):
        return {} if self.model_data is None else self.model_data["Arena"]

    def setModel(self, model):
        self.reference_model = model

    def getReferenceData(self):
        return None if self.model_data is None else self.model_data["ReferenceModel"]

    def addSkill(self, skill):
        self.selected_skills.append(skill)

    def removeSkill(self, skill):
        if skill in self.selected_skills:
            self.selected_skills.remove(skill)

    def addBehaviour(self, behaviour):
        if behaviour not in self.behaviours:
            self.behaviours.append(behaviour)

    def removeBehaviour(self, behaviour):
        if behaviour in self.behaviours:
            self.behaviours.remove(behaviour)


class MissionView(QWidget):
    """
    UI for a mission
    """
    def __init__(self):
        super(MissionView, self).__init__()

        ResourceLoader.loadWidget("MissionView.ui", self)
        self.skillLayout: QVBoxLayout = self.SkillBoxContents.layout()
        self.skillLayout.setAlignment(Qt.AlignTop)

        self.behaviourLayout: QVBoxLayout = self.BehaviourBoxContents.layout()
        self.behaviourLayout.setAlignment(Qt.AlignTop)

    def addSkill(self, skill_view):
        self.skillLayout.addWidget(skill_view.skillItem)

    def addBehaviour(self, behaviour_view):
        self.behaviourLayout.addWidget(behaviour_view.behaviourItem)

    def setSelectedItem(self, item):
        pass

    def setCenterPanel(self, view):
        self.CenterPanel.setCurrentWidget(view)

    def registerToCenterPanel(self, view):
        self.CenterPanel.addWidget(view)

    def addSettingsTab(self, view, name):
        self.SettingsTabs.addTab(view, name)


class MissionController:
    """
    Controller for the current opened mission
    """
    def __init__(self):
        self.mission_view = MissionView()
        self.current_mission = None

        self.arenaController = ArenaController()
        self.robotModelController = RobotModelController()
        self.robotModelController.modelChanged += self.update_robot_model

        self.mission_view.registerToCenterPanel(self.arenaController.view)
        self.arenaController.onArenaSelected += self.onItemSelected
        self.mission_view.addSettingsTab(self.arenaController.getTab(), "Arena")
        self.mission_view.addSettingsTab(QWidget(), "Mission")
        self.mission_view.addSettingsTab(self.robotModelController.getTab(), "Model")

        self.skillControllers = {}  # skill controllers mapped to the id of their skill
        self.behaviourControllers = {}  # behaviour controllers mapped to the id of their behaviour
        self.loadModel("model.json")

        self.selectedItem = None

    def createMission(self, data=None):
        # TODO : check if there already is a mission open
        self.setCurrentMission(Mission(data))

    def setCurrentMission(self, mission):
        self.current_mission = mission
        self.update_behaviours(mission.getBehaviourData())
        self.update_skills(mission.getSkillData())
        self.update_arena(mission.arena)
        self.update_robot_model(mission.getReferenceData())

    def update_robot_model(self, reference):
        self.robotModelController.setModel(reference)
        if self.current_mission:
            self.current_mission.setModel(self.robotModelController.current)

    def update_skills(self, skill_data):
        if skill_data is not None:
            for data in skill_data:
                skill_id = data["id"]
                if skill_id not in self.skillControllers:
                    continue

                controller = self.skillControllers[skill_id]
                controller.loadFromData(data)
                controller.onAdded(True)

    def update_behaviours(self, behaviour_data):
        if behaviour_data is not None:
            for data in behaviour_data:
                behaviour_id = data["id"]
                if behaviour_id not in self.behaviourControllers:
                    continue

                controller = self.behaviourControllers[behaviour_id]
                controller.loadFromData(data)

    def update_arena(self, arena):
        self.arenaController.setArena(arena)

    def getMissionData(self):
        if self.current_mission is None:
            return {}
        return self.current_mission.toJson()

    def getView(self):
        return self.mission_view

    def hasCurrentMission(self):
        return self.current_mission is not None

    def loadModel(self, model_path):
        with ResourceLoader.openData(model_path) as model_file:
            try:
                model_data = json.load(model_file)
                self.loadSkills(model_data)
                self.loadBehaviours(model_data)
                self.loadRobotModels(model_data)

            except json.JSONDecodeError:
                displayError("Invalid Model File", "The model could not be loaded properly.")

    def loadRobotModels(self, model_data):
        self.robotModelController.loadModels(model_data["ReferenceModels"])

    def loadSkills(self, model_data):
        for skill_def in model_data["Skills"]:
            self.createSkill(skill_def)

    def createSkill(self, data):
        # print("first loading", data)
        skill = Skill(data)
        controller = SkillController(skill)
        controller.onSkillSelected += self.onSkillSelected
        controller.onSkillAdded += self.onSkillAdded

        self.skillControllers[skill.id] = controller
        self.mission_view.addSkill(controller.getView())
        self.addCenterPanelPage(controller)

    def onSkillAdded(self, skill, checked):
        if checked:
            self.current_mission.addSkill(skill)
            for b_id in skill.behaviours:
                controller = self.behaviourControllers[b_id]
                controller.setActive(True)
                self.current_mission.addBehaviour(controller.behaviour)
        else:
            self.current_mission.removeSkill(skill)

            ids = [s.id for s in self.current_mission.selected_skills if s.active]
            for b_id in skill.behaviours:
                controller = self.behaviourControllers[b_id]
                for s_id in controller.behaviour.skills:
                    if s_id in ids:
                        return
                controller.setActive(False)
                self.current_mission.removeBehaviour(controller.behaviour)

    def loadBehaviours(self, model_data):
        for behaviour_def in model_data["Behaviours"]:
            self.createBehaviour(behaviour_def)

    def createBehaviour(self, data):  # TODO : very similar to createSkill, see how to merge them
        behaviour = Behaviour(data)
        controller = BehaviourController(behaviour)
        controller.onBehaviourSelected += self.onItemSelected

        self.behaviourControllers[behaviour.id] = controller
        self.mission_view.addBehaviour(controller.getView())  # TODO : all view stuff at once
        self.addCenterPanelPage(controller)

        for skill_id in behaviour.skills:
            self.skillControllers[skill_id].skill.linkBehaviour(behaviour.id)

    def addCenterPanelPage(self, controller):
        view = controller.getView()
        self.mission_view.registerToCenterPanel(view.getCenterWidget())

    def onItemSelected(self, item):  # TODO : interface for item and itemView ?
        # item is a controller that can be selected/unselected and displayed in the center panel

        for b_id in self.behaviourControllers:
            self.behaviourControllers[b_id].setHighlighted(False)

        view = item.getView()

        if self.selectedItem is not None:
            # self.mission_view.unselectItem(view.getSideWidget())
            self.selectedItem.setSelected(False)
        # self.mission_view.selectedItem(view.getSideWidget())
        item.setSelected(True)

        self.selectedItem = item
        widget = view.getCenterWidget()
        self.mission_view.setCenterPanel(widget)

    def onSkillSelected(self, skillController):
        self.onItemSelected(skillController)

        for b_id in skillController.skill.behaviours:
            self.behaviourControllers[b_id].setHighlighted(True)

    def selectArena(self):
        self.onItemSelected(self.arenaController)
