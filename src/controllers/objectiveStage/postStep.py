from src.controllers.objectiveStage.stage import StageController, FunctionSelectorController
from src.util import Event


class PostStepStageController(StageController):
    def __init__(self, view):
        super().__init__(view)
        self.onIncrementChanged = Event()

    def onViewChanged(self, **kwargs):
        super(PostStepStageController, self).onViewChanged(**kwargs)

        if "increment" in kwargs:
            self.onIncrementChanged()

    # ---------- Events ------------

    def onStageAdded(self, stage):
        if self.stages is None:
            return
        super(PostStepStageController, self).onStageAdded(stage)
        self.onIncrementChanged()

    def onStageRemoved(self, index):
        if self.stages is None:
            return
        super(PostStepStageController, self).onStageRemoved(index)
        self.onIncrementChanged()
