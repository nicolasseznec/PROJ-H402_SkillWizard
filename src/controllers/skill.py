from src.models.skill import Skill
from src.util import Event
from src.views.skill import SkillView, SkillParameterView


class SkillController:
    """
    Controller for a robot skill.
    """
    def __init__(self, skill, view):
        self.skill = skill
        self.view = view
        self.parameterControllers = []
        self.createParameterControllers()

        self.view.updateView(skill)
        self.view.onSelected += self.onViewSelected
        self.view.onChecked += self.onViewChecked

        self.onSelected = Event()
        self.onChecked = Event()

    def getCenterWidget(self):
        """
        Returns the main panel (the skill inspector).
        """
        return self.view.getCenterWidget()

    def updateView(self):
        """
        Update the view contents to the skill.
        """
        self.view.updateView(self.skill)
        for controller in self.parameterControllers:
            controller.updateView()

    def getBehaviorsIds(self):
        return self.skill.behaviors

    # ---------- Events ------------

    def onViewSelected(self):
        """
        Called when the skill is selected in the side panel.
        """
        self.onSelected(self)

    def onViewChecked(self, checked):
        """
        Called when the skill is enabled or disabled.
        """
        self.setChecked(checked)
        self.skill.setActive(checked)
        self.onChecked(self.skill, checked)
        # TODO : better visual feedback

    # -----------------------------

    def setChecked(self, checked):
        self.view.setChecked(checked)

    def setSelected(self, selected):
        self.view.setSelected(selected)

    def createParameterControllers(self):
        """
        Create every parameter for this skill
        """
        for param in self.skill.parameters.values():
            controller = SkillParameterController(param)
            self.parameterControllers.append(controller)
            self.view.addParameter(controller.view)

    def reset(self):
        """
        Resets the skill and its parameters to a blank state.
        """
        self.skill.reset()
        self.updateView()


class SkillParameterController:
    """
    Controller for a generic behavior parameter. Creates a specific view depending in the parameters's type.
    """
    def __init__(self, parameter):
        self.parameter = parameter
        self.view = SkillParameterView(parameter)
        self.view.onParameterChanged += self.updateParameter

    def updateParameter(self):
        self.parameter.resolution = self.view.Resolution.value()
        self.parameter.accuracy = self.view.Accuracy.value()
        self.parameter.responseTime = self.view.ResponseTime.value()

    def updateView(self):
        self.view.updateView(self.parameter)


class SkillLoader:
    """
    Loader for the skills. Creates every skills given a model, and connects its events.
    """
    @staticmethod
    def loadSkills(modelData, registerSkill, onSelected, onChecked):
        for data in modelData["Skills"]:
            item = Skill(data)
            view = SkillView()
            controller = SkillController(item, view)  # TODO : ensure that everything is passed by reference
            controller.onSelected += onSelected
            controller.onChecked += onChecked

            registerSkill(item, view, controller)
