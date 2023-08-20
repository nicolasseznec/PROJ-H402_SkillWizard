import json

from src.controllers.utils.itemList import SingleItemListController
from src.models.objectiveUtils.stage import Stage
from src.util import Event, ResourceLoader


class StageController:
    def __init__(self, view):
        self.view = view
        self.currentStage = None
        self.stages = None

        self.view.onStageChanged += self.onViewChanged
        self.stageListController = self.createStageListController(self.view.stageListView)
        self.stageListController.onItemAdded += self.onStageAdded
        self.stageListController.onItemRemoved += self.onStageRemoved
        self.stageListController.onItemSelected += self.onStageSelected

    def createStageListController(self, view):
        return StageListController(view)

    def setStage(self, stage):
        self.currentStage = stage
        if stage is not None:
            self.updateView()

    def setStageList(self, stages):
        self.stages = stages
        self.stageListController.loadStages(stages)
        if stages:
            self.setStage(self.stages[0])

    def updateView(self):
        self.view.updateView(self.currentStage)

    def updateName(self, index):
        self.stages[index].loadFromData({"name": Stage.getNameFromIndex(index)})
        self.stageListController.setItemText(index, self.stageListController.getNameFromIndex(index))

    # ---------- Events ------------

    def onStageAdded(self, stage):
        if self.stages is None:
            return

        self.stages.append(stage)
        self.onStageSelected(len(self.stages) - 1)

    def onStageRemoved(self, index):
        if not self.stages or index < 0:
            return

        self.stages.pop(index)
        if self.stages:
            for i in range(len(self.stages)):
                self.updateName(i)
            self.onStageSelected(max(0, index - 1))
        else:
            self.view.clear()

    def onStageSelected(self, index):
        self.stageListController.selectRow(index)
        if self.stages:
            self.setStage(self.stages[index])

    def onViewChanged(self, **kwargs):
        if self.currentStage is not None:
            self.currentStage.loadFromData(kwargs)


# --------------------------

class StageListController(SingleItemListController):
    def createNewItem(self):
        return Stage({
            "name": Stage.getNameFromIndex(self.view.count())
        })

    def getDefaultName(self):
        return self.getNameFromIndex(self.view.count())

    def getNameFromIndex(self, index):
        return "Stage {}".format(index)

    def selectRow(self, index):
        self.view.selectRow(index)

    def setItemText(self, index, text):
        self.view.setItemText(index, text)

    def loadStages(self, stages):
        self.view.clear()
        for _ in stages:
            self.view.addItem(self.getDefaultName())


# --------------------------

class FunctionSelectorController:
    def __init__(self, view):
        self.view = view
        self.view.onInsert += self.onInsert
        self.view.onFunctionSelected += self.onFunctionSelected
        self.view.onVariableSelected += self.onVariableSelected

        self.selection = None
        self.selectionType = None
        self.onCodeInserted = Event()

        self.functions = {}
        self.variables = []
        self.loadElements()
        self.setupView()

        self.updateView()

    def updateView(self):
        description = ""
        name = ""

        if self.selectionType == "func":
            description = self.selection["description"]
            name = self.selection["call"]
        elif self.selectionType == "var":
            description = f'{self.selection["description"]}\n\nType: {self.selection["type"]}'
            name = self.selection["name"]

        self.view.updateView(name, description)

    def setupView(self):
        for func in self.functions:
            self.view.addFunction(func["call"])
        for var in self.variables:
            self.view.addVariable(var["name"])

    # ---------- Events ------------

    def onInsert(self):
        if self.selection is None:
            return
        self.onCodeInserted(self.selection, self.selectionType)

    def onFunctionSelected(self, index):
        self.selection = self.functions[index]
        self.selectionType = "func"
        self.updateView()

    def onVariableSelected(self, index):
        self.selection = self.variables[index]
        self.selectionType = "var"
        self.updateView()

    # --------------------------

    def loadElements(self):
        with ResourceLoader.openData("objective_model.json") as functionFile:
            modelData = json.load(functionFile)
            for func in modelData["functions"]:
                call = func["call"]
                if call in self.functions:
                    self.functions[call]["description"] += f'\n\nOverload {func["arguments"]} : {func["description"]}'
                else:
                    self.functions[call] = func
                    self.functions[call]["description"] = f'Arguments {func["arguments"]} : {func["description"]}'

            self.functions = list(self.functions.values())
            self.variables = modelData["variables"]
