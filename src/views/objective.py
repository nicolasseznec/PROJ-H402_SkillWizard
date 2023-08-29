from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout

from src.util import ResourceLoader, Event
from src.views.objectiveStage.initStage import InitStageView
from src.views.objectiveStage.postExp import PostExpStageView
from src.views.objectiveStage.postStep import PostStepStageView


class ObjectiveView(QGroupBox):
    """
    View for objective editor and the objective settings tab.
    """
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("ObjectiveInspector.ui", self)
        self.settingsTab = ResourceLoader.loadWidget("ObjectiveSettingsTab.ui")

        self.onObjectiveClicked = Event()
        self.onGenerateClicked = Event()
        self.onObjectiveSettingsChanged = Event()

        self.postStepView = PostStepStageView(self)
        self.addToLayout(self.postStepView, self.PostStepStage)
        self.postExpView = PostExpStageView(self)
        self.addToLayout(self.postExpView, self.PostExpStage)
        self.initView = InitStageView(self)
        self.addToLayout(self.initView, self.InitStage)

        self.blockSignal = False
        self.connectActions()

    def connectActions(self):
        self.settingsTab.EditObjectiveButton.clicked.connect(self.onEditObjective)
        self.settingsTab.GenerateLoopFunctionsButton.clicked.connect(self.onGenerateLoopFunctions)
        self.settingsTab.ObjectiveName.editingFinished.connect(self.onObjectiveNameChanged)

    def getCenterWidget(self):
        return self

    def updateView(self, objective):
        """
        Update the view contents with the new objective.
        """
        self.updatePostStepFunction(objective.postStepStages)
        self.updatePostExpFunction(objective.postExpStages)
        self.settingsTab.ObjectiveName.setText(objective.name)

    # ---------- Events ------------

    def onEditObjective(self):
        """
        Called when the user clicks on edit objective.
        """
        if self.blockSignal:
            return
        self.onObjectiveClicked()

    def onGenerateLoopFunctions(self):
        """
        Called when the user clicks on generatae loop functions
        """
        if self.blockSignal:
            return
        self.onGenerateClicked()

    def onObjectiveNameChanged(self):
        """
        Called when the name of the objective has been changed
        """
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
        """
        Sets the Post Step function text. See getFunctionFromStages
        """
        self.PostStepFunction.setText(self.getFunctionFromStages(stages, "0"))

    def updatePostExpFunction(self, stages):
        """
        Sets the Post Experiment function text. See getFunctionFromStages
        """
        self.PostExpFunction.setText(self.getFunctionFromStages(stages, "objective"))

    def getFunctionFromStages(self, stages, default=""):
        """
        Creates the text of the function expression from the list of stages.
        For instance, if the list contains 3 stages but the second one does not count in the final function (increment
        is set to false), the output will be : "stage0 + stage2"

        If not stage should count, the output is set to default
        """
        first = True
        function = ""
        for stage in stages:
            if stage.increment:
                if not first:
                    function += " + "
                function += stage.name
                first = False

        if first:  # no stages are active
            function = default

        return function
