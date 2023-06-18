from PyQt5.QtWidgets import QWidget

from src.util import DataContainer, ResourceLoader, Event


class RobotModel(DataContainer):
    # Reference model
    def __init__(self, data):
        self.model = "None"
        super(RobotModel, self).__init__(data)

    def getAttributes(self):
        return {
            "model": "None",
            "name": "None",
            "desc": "[...]"
        }

    def toJson(self):
        return self.model


class RobotModelView(QWidget):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ModelSettingsTab.ui", self)
        self.onModelChanged = Event()
        self.RobotModel.currentIndexChanged.connect(self.modelChanged)

    def addModel(self, reference):
        self.RobotModel.addItem(reference)

    def modelChanged(self, index):
        self.onModelChanged(self.RobotModel.currentText())

    def updateView(self, model):
        self.ModelDescription.setText(model.desc)


class RobotModelController:
    def __init__(self):
        self.models = {}
        self.current = None
        self.view = RobotModelView()
        self.view.onModelChanged += self.setModel

    def loadModels(self, data):
        for model in data:
            self.models[model["model"]] = RobotModel(model)
            self.view.addModel(model["model"])  # add element to view

        if self.models:
            self.current = next(iter(self.models.values()))  # select the "first" element as default
            self.view.updateView(self.current)

    def setModel(self, reference):
        # print(reference)
        if reference in self.models:
            self.current = self.models[reference]
            self.view.updateView(self.current)
            # TODO : notify mission controller, to update model object in the mission

        # print(self.models.keys())

    def getTab(self):
        return self.view
