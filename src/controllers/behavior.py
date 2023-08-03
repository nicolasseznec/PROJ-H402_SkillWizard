from src.models.behavior import Behavior
from src.util import Event
from src.views.behavior import BehaviorView, BehaviorParameterView, BpColorView, BpIntView, BpFloatView


class BehaviorController:
    def __init__(self, behavior, view):
        self.behavior = behavior
        self.view = view

        self.parameterControllers = []
        self.createParameterControllers()

        self.view.updateView(behavior)
        self.view.onSelected += self.onSelected
        self.behavior.onActived += self.onActivated
        self.onBehaviourSelected = Event()

    def getView(self):
        return self.view

    def updateView(self):
        self.view.updateView(self.behavior)
        for controller in self.parameterControllers:
            controller.updateView()

    # ---------------- Events -----------------

    def onActivated(self, active):
        self.view.setActive(active)

    def onSelected(self):
        self.onBehaviourSelected(self)

    # -----------------------------------------

    def setActive(self, active):
        self.behavior.setActive(active)

    def setSelected(self, selected):
        self.view.setSelected(selected)

    def setHighlighted(self, highlighted):
        self.view.setHighlighted(highlighted)

    def createParameterControllers(self):
        for param in self.behavior.parameters.values():
            controller = BehaviorParameterController(param)
            self.parameterControllers.append(controller)
            self.view.addParameter(controller.view)

    def reset(self):
        self.behavior.reset()
        self.updateView()


class BehaviorParameterController:
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
    @staticmethod
    def loadBehaviors(modelData, registerBehavior, onSelected):
        for data in modelData["Behaviors"]:
            item = Behavior(data)
            view = BehaviorView()
            controller = BehaviorController(item, view)
            controller.onSelected += onSelected

            registerBehavior(item, view, controller)
