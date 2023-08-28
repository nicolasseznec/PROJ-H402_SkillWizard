from src.models.robot import RobotModel
from src.util import Event
from src.views.robot import RobotModelView


class RobotModelController:
    """
    Controller for the robot reference model
    """
    def __init__(self, view: RobotModelView):
        self.models = {}
        self.current = None
        self.view = view
        self.modelChanged = Event()
        self.view.onModelChanged += self.modelChanged

    def setModel(self, reference):
        """
        Update the view to the new selected model given its reference
        """
        if reference in self.models:
            self.current = self.models[reference]
            self.view.updateView(self.current)

    def addModel(self, model):
        """
        Adds a new reference model
        """
        self.models[model.reference] = model
        self.view.addModel(model.reference)

    def getTab(self):
        return self.view


class RobotModelLoader:
    """
    Loader for the reference models. Creates every reference models.
    """
    @staticmethod
    def loadModels(modelData, controller: RobotModelController):
        for model in modelData["ReferenceModels"]:
            controller.addModel(RobotModel(model))
