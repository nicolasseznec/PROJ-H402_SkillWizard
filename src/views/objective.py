from PyQt5.QtWidgets import QGroupBox

from src.util import ResourceLoader, Event


class ObjectiveView(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ObjectiveInspector.ui", self)
        self.settingsTab = ResourceLoader.loadWidget("ObjectiveSettingsTab.ui")

        self.onObjectiveClicked = Event()
        self.onGenerateClicked = Event()
        self.onObjectiveSettingsChanged = Event()

        self.blockSignal = False
        self.connectActions()

    def connectActions(self):
        self.settingsTab.EditObjectiveButton.clicked.connect(self.onEditObjective)
        self.settingsTab.GenerateLoopFunctionsButton.clicked.connect(self.onGenerateLoopFunctions)
        self.settingsTab.ObjectiveName.editingFinished.connect(self.onObjectiveNameChanged)

    def getCenterWidget(self):
        return self

    def updateView(self, objective):
        pass

    # ---------- Events ------------

    def onEditObjective(self):
        if self.blockSignal:
            return
        self.onObjectiveClicked()

    def onGenerateLoopFunctions(self):
        if self.blockSignal:
            return
        self.onGenerateClicked()

    def onObjectiveNameChanged(self):
        if self.blockSignal:
            return
        self.onObjectiveSettingsChanged(name=self.settingsTab.ObjectiveName.text())
