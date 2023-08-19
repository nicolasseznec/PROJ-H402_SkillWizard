from src.util import ResourceLoader
from src.views.objectiveStage.postStep import PostStepStageView
from src.views.objectiveStage.stage import StageListView


class PostExpStageView(PostStepStageView):
    def loadWidget(self):
        ResourceLoader.loadWidget("objective/PostExpStage.ui", self)

    def createStageListView(self, container):
        return PostExpStageListView(container)


class PostExpStageListView(StageListView):
    def getWidgets(self, settingsContainer):
        return settingsContainer.PostExpAddButton, settingsContainer.PostExpRemoveButton, settingsContainer.PostExpStageList
