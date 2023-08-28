from src.models.behavior import Behavior
from src.util import Event
from src.views.behavior import BehaviorView, BehaviorParameterView, BpColorView, BpIntView, BpFloatView


class BehaviorController:
    """
    Controller for a robot behavior.
    """
    def __init__(self, behavior, view):
        self.behavior = behavior
        self.view = view

        self.parameterControllers = []
        self.createParameterControllers()

        self.view.updateView(behavior)
        self.view.onSelected += self.onViewSelected
        self.behavior.onActived += self.onActivated
        self.onSelected = Event()

    def getCenterWidget(self):
        """
        Returns the main panel (the behavior inspector).
        """
        return self.view.getCenterWidget()

    def updateView(self):
        """
        Update the view contents to the behavior.
        """
        self.view.updateView(self.behavior)
        for controller in self.parameterControllers:
            controller.updateView()

    # ---------------- Events -----------------

    def onActivated(self, active):
        """
        Called when the behavior is enabled or disabled.
        """
        self.view.setActive(active)

    def onViewSelected(self):
        """
        Called when the behavior is selected in the side panel.
        """
        self.onSelected(self)

    # -----------------------------------------

    def setActive(self, active):
        self.behavior.setActive(active)

    def setSelected(self, selected):
        self.view.setSelected(selected)

    def setHighlighted(self, highlighted):
        self.view.setHighlighted(highlighted)

    def createParameterControllers(self):
        """
        Create every parameter for this behavior
        """
        for param in self.behavior.parameters.values():
            controller = BehaviorParameterController(param)
            self.parameterControllers.append(controller)
            self.view.addParameter(controller.view)

    def reset(self):
        """
        Resets the behavior and its parameters to a blank state.
        """
        self.behavior.reset()
        self.updateView()


class BehaviorParameterController:
    """
    Controller for a generic behavior parameter. Creates a specific view depending in the parameters's type.
    """
    def __init__(self, parameter):
        self.parameter = parameter

        if parameter.type == "color":
            self.view = BpColorView(parameter)
        elif parameter.type == "int":
            self.view = BpIntView(parameter)
        elif parameter.type == "float":
            self.view = BpFloatView(parameter)
        else:
            self.view = BehaviorParameterView(parameter)

        self.view.onParameterChanged += self.updateParameter

    def updateParameter(self):
        self.parameter.update(self.view.getValues())

    def updateView(self):
        self.view.updateView(self.parameter)


class BehaviorLoader:
    """
    Loader for the behaviors. Creates every behavior given a model, and connects its events.
    """
    @staticmethod
    def loadBehaviors(modelData, registerBehavior, onSelected):
        for data in modelData["Behaviors"]:
            item = Behavior(data)
            view = BehaviorView()
            controller = BehaviorController(item, view)
            controller.onSelected += onSelected

            registerBehavior(item, view, controller)
