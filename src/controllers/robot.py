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

    def setModel(self, reference):
        if reference in self.models:
            self.current = self.models[reference]
            self.view.updateView(self.current)

    def addModel(self, model):
        self.models[model.reference] = model
        self.view.addModel(model.reference)

    def getTab(self):
        return self.view


class RobotModelLoader:
    @staticmethod
    def loadModels(modelData, controller: RobotModelController):
        for model in modelData["ReferenceModels"]:
            controller.addModel(RobotModel(model))
