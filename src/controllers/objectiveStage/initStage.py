from src.controllers.objectiveStage.stage import StageController, StageListController
from src.models.objectiveUtils.stage import Stage


class InitStageController(StageController):
    """
    Controller for the Init function.
    """
    def __init__(self, view):
        super().__init__(view)

    def onViewChanged(self, **kwargs):
        super(InitStageController, self).onViewChanged(**kwargs)

        if "name" in kwargs:
            self.stageListController.setCurrentText(kwargs["name"])
            self.view.setIdentifier(kwargs["name"])

    def createStageListController(self, view):
        return InitVariableListController(view)

    def onStageRemoved(self, index):
        if not self.stages or index < 0:
            return

        self.stages.pop(index)
        if self.stages:
            self.onStageSelected(max(0, index - 1))
        else:
            self.view.clear()


class InitVariableListController(StageListController):
    """
    controller for the Init variables list.
    """
    def getNameFromIndex(self, index):
        return f"NewVariable_{index}"

    def createNewItem(self):
        return Stage({
            "name": f"NewVariable_{self.view.count()}"
        })
