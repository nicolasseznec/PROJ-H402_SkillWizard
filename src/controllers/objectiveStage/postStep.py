from src.controllers.objectiveStage.stage import StageController, FunctionSelectorController
from src.util import Event


class PostStepStageController(StageController):
    def __init__(self, view):
        super().__init__(view)
        self.onIncrementChanged = Event()

        self.functionSelectorController = FunctionSelectorController(self.view.functionSelectorView)
        self.functionSelectorController.onCodeInserted += self.onCodeInserted

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

    def onCodeInserted(self, element, elementType):
        name = element.get("call", element["name"])
        code = ""
        if elementType == "func":
            code = f"{name}(\n"
            first = True
            for _ in element["arguments"]:
                if not first:
                    code += " ,\n"
                first = False
            code += "\n)"
        elif elementType == "var":
            code = name

        self.view.insertCode(code)

        # print("Insert", elementType, ":", code)

