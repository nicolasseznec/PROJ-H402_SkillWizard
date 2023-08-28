from src.util import ResourceLoader
from src.views.objectiveStage.stage import StageView, StageListView


class PostStepStageView(StageView):
    """
    View for the Post Step function and its stage inspector.
    """
    def __init__(self, container, *__args):
        super().__init__(container, *__args)
        self.IncrementCheckBox.clicked.connect(self.incrementClicked)

    def loadWidget(self):
        ResourceLoader.loadWidget("objective/PostStepStage.ui", self)

    def createStageListView(self, container):
        return PostStepStageListView(container)

    def updateView(self, stage):
        self.blockSignals = True
        self.IncrementCheckBox.setChecked(stage.increment)
        super(PostStepStageView, self).updateView(stage)

    # ---------- Events ------------

    def incrementClicked(self, checked):
        self.onStageChanged(increment=checked)


class PostStepStageListView(StageListView):
    def getWidgets(self, settingsContainer):
        return settingsContainer.PostStepAddButton, settingsContainer.PostStepRemoveButton, settingsContainer.PostStepStageList
