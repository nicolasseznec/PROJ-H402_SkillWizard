from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout

from src.util import ResourceLoader, Event
from src.views.objectiveStage.postStep import PostStepStageView


class ObjectiveView(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ObjectiveInspector.ui", self)
        self.settingsTab = ResourceLoader.loadWidget("ObjectiveSettingsTab.ui")

        self.onObjectiveClicked = Event()
        self.onGenerateClicked = Event()
        self.onObjectiveSettingsChanged = Event()

        self.postStepView = PostStepStageView(self)
        self.addToLayout(self.postStepView, self.PostStepStage)

        self.blockSignal = False
        self.connectActions()

    def connectActions(self):
        self.settingsTab.EditObjectiveButton.clicked.connect(self.onEditObjective)
        self.settingsTab.GenerateLoopFunctionsButton.clicked.connect(self.onGenerateLoopFunctions)
        self.settingsTab.ObjectiveName.editingFinished.connect(self.onObjectiveNameChanged)

    def getCenterWidget(self):
        return self

    def updateView(self, objective):
        self.updatePostStepFunction(objective.postStepStages)

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

    # ----------------------

    def addToLayout(self, widget, parent):
        layout = QVBoxLayout()
        layout.addWidget(widget, alignment=Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        parent.setLayout(layout)

    def updatePostStepFunction(self, stages):
        self.PostStepFunction.setText(self.getFunctionFromStages(stages))

    def getFunctionFromStages(self, stages):
        first = True
        function = ""
        for stage in stages:
            if stage.increment:
                if not first:
                    function += " + "
                function += stage.name
                first = False
        return function
