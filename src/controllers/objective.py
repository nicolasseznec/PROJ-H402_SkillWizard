from src.controllers.objectiveStage.initStage import InitStageController
from src.controllers.objectiveStage.postExp import PostExpStageController
from src.controllers.objectiveStage.postStep import PostStepStageController
from src.util import Event
from src.views.objective import ObjectiveView


class ObjectiveController:
    """
    Controller for the objective editor and its settings tab.
    """
    def __init__(self, view: ObjectiveView):
        self.view = view
        self.objective = None

        self.onSelected = Event()
        self.onGenerateClicked = Event()

        self.postStepController = PostStepStageController(view.postStepView)
        self.postStepController.onIncrementChanged += self.updatePostStepFunction
        self.postExpController = PostExpStageController(view.postExpView)
        self.postExpController.onIncrementChanged += self.updatePostExpFunction
        self.initController = InitStageController(view.initView)

        self.view.onObjectiveClicked += self.onViewClicked
        self.view.onObjectiveSettingsChanged += self.onSettingsChanged

    def getCenterWidget(self):
        return self.view.getCenterWidget()

    # ---------- Events ------------

    def onViewClicked(self):
        """
        Called when the user clicks on edit objective.
        """
        self.onSelected(self)

    def onSettingsChanged(self, **kwargs):
        """
        Called when one of the objective settings changed. All changed settings are given in kwargs. Updates the current
        objective with the new settings.
        """
        if self.objective is not None:
            self.objective.loadFromData(kwargs)

    def updatePostStepFunction(self):
        """
        Called when a stage has been add/removed. Updates the post step function expression.
        """
        self.view.updatePostStepFunction(self.objective.postStepStages)

    def updatePostExpFunction(self):
        """
        Called when a stage has been add/removed. Updates the post experiment function expression.
        """
        self.view.updatePostExpFunction(self.objective.postExpStages)

    # ------------------------------

    def setSelected(self, selected):
        pass

    def setObjective(self, objective):
        """
        Update all controllers (and their views) to a new objective.
        """
        self.objective = objective

        if objective is not None:
            self.postStepController.setStageList(objective.postStepStages)
            self.postExpController.setStageList(objective.postExpStages)
            self.initController.setStageList(objective.initStages)
            self.view.updateView(objective)

    def setFunctionGenerator(self, functionGenerator):
        """
        Connects the function generatior to the view.
        """
        self.view.onGenerateClicked.clear()
        self.view.onGenerateClicked += functionGenerator
