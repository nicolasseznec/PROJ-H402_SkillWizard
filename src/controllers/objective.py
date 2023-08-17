from src.controllers.objectiveStage.postStep import PostStepStageController
from src.util import Event
from src.views.objective import ObjectiveView


class ObjectiveController:
    def __init__(self, view: ObjectiveView):
        self.view = view
        self.objective = None

        self.onSelected = Event()
        self.onGenerateClicked = Event()

        self.postStepController = PostStepStageController(view.postStepView)
        self.postStepController.onIncrementChanged += self.updatePostStepFunction

        self.view.onObjectiveClicked += self.onViewClicked
        self.view.onObjectiveSettingsChanged += self.onSettingsChanged

    def getCenterWidget(self):
        return self.view.getCenterWidget()

    # ---------- Events ------------

    def onViewClicked(self):
        self.onSelected(self)

    def onSettingsChanged(self, **kwargs):
        if self.objective is not None:
            self.objective.loadFromData(kwargs)

    def updatePostStepFunction(self):
        self.view.updatePostStepFunction(self.objective.postStepStages)

    # ------------------------------

    def setSelected(self, selected):
        pass

    def setObjective(self, objective):
        self.objective = objective

        if objective is not None:
            self.postStepController.setStageList(objective.postStepStages)
            self.view.updateView(objective)

    def setFunctionGenerator(self, functionGenerator):
        self.view.onGenerateClicked.clear()
        self.view.onGenerateClicked += functionGenerator