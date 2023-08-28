from PyQt5.QtWidgets import QWidget

from src.util import ResourceLoader, Event


class RobotModelView(QWidget):
    """
    View for the robot reference model settings tab.
    """
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ModelSettingsTab.ui", self)
        self.onModelChanged = Event()
        self.RobotModel.currentIndexChanged.connect(self.modelChanged)

    def addModel(self, reference):
        """
        Add a new selectable model.
        """
        self.RobotModel.addItem(reference)

    def modelChanged(self, index):
        """
        Called when the current model has been changed.
        """
        self.onModelChanged(self.RobotModel.currentText())

    def updateView(self, model):
        """
        Upadtes the displayed information from the given model
        """
        self.ModelDescription.setText(model.desc)
        self.ModelInfo.setTitle(model.name)

        self.RobotModel.blockSignals(True)
        self.RobotModel.setCurrentIndex(self.RobotModel.findText(model.reference))
        self.RobotModel.blockSignals(False)
