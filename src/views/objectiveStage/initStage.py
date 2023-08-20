from src.util import ResourceLoader, cleanIdentifier
from src.views.objectiveStage.stage import StageView, StageListView


class InitStageView(StageView):
    def loadWidget(self):
        ResourceLoader.loadWidget("objective/InitStage.ui", self)
        self.StageName = self.VariableName
        self.VariableName.editingFinished.connect(self.variableChanged)

    def createStageListView(self, container):
        return InitStageListView(container)

    def updateView(self, stage):
        self.blockSignals = True
        self.StageName.setText(stage.name)
        self.setIdentifier(stage.name)
        self.CodeArea.setPlainText(stage.code)
        self.blockSignals = False
        self.setEnabled(True)

    def setIdentifier(self, name):
        self.IdentifierLabel.setText(f"Identifier : {cleanIdentifier(name)}")

    # ---------- Events ------------

    def variableChanged(self):
        self.onStageChanged(name=self.VariableName.text())


class InitStageListView(StageListView):
    def getWidgets(self, settingsContainer):
        return settingsContainer.InitAddButton, settingsContainer.InitRemoveButton, settingsContainer.InitStageList
