from src.models.robot import RobotModel
from src.util import Event
from src.views.robot import RobotModelView


class RobotModelController:
    def __init__(self, view: RobotModelView):
        self.models = {}
        self.current = None
        self.view = view
        self.modelChanged = Event()
        self.view.onModelChanged += self.modelChanged

    def loadModels(self, data):
        for model in data:
            self.models[model["model"]] = RobotModel(model)
            self.view.addModel(model["model"])  # add element to view

        if self.models:
            self.current = next(iter(self.models.values()))  # select the "first" element as default
            self.view.updateView(self.current)

    def setModel(self, reference):
        if reference in self.models:
            self.current = self.models[reference]
            self.view.updateView(self.current)

    def getTab(self):
        return self.view


class RobotModelLoader:
    @staticmethod
    def loadModels(modelData, controller: RobotModelController):
        controller.loadModels(modelData["ReferenceModels"])
