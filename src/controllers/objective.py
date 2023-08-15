from src.util import Event
from src.views.objective import ObjectiveView


class ObjectiveController:
    def __init__(self, view: ObjectiveView):
        self.view = view
        self.objective = None

        self.onSelected = Event()
        self.onGenerateClicked = Event()

        self.view.onObjectiveClicked += self.onViewClicked
        self.view.onGenerateClicked += self.onGenerateClicked
        self.view.onObjectiveSettingsChanged += self.onSettingsChanged

    def getCenterWidget(self):
        return self.view.getCenterWidget()

    # ---------- Events ------------

    def onViewClicked(self):
        self.onSelected(self)

    def onSettingsChanged(self, **kwargs):
        if self.objective is not None:
            self.objective.loadFromData(kwargs)

    # ------------------------------

    def setSelected(self, selected):
        pass

    def setObjective(self, objective):
        self.objective = objective

        if objective is not None:
            self.view.updateView(objective)
