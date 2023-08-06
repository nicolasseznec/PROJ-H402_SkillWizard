from PyQt5.QtWidgets import QWidget

from src.util import ResourceLoader, Event


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
        self.ModelInfo.setTitle(model.name)

        self.RobotModel.blockSignals(True)
        self.RobotModel.setCurrentIndex(self.RobotModel.findText(model.reference))
        self.RobotModel.blockSignals(False)
