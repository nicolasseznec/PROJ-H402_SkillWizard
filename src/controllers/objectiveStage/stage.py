import json

from src.controllers.utils.itemList import SingleItemListController
from src.models.objectiveUtils.stage import Stage
from src.util import Event, ResourceLoader


class StageController:
    """
    Base Controller for the objective's stages.
    Contains the list of stages and the current selected stage.
    """
    def __init__(self, view):
        self.view = view
        self.currentStage = None
        self.stages = None

        self.view.onStageChanged += self.onViewChanged
        self.stageListController = self.createStageListController(self.view.stageListView)
        self.stageListController.onItemAdded += self.onStageAdded
        self.stageListController.onItemRemoved += self.onStageRemoved
        self.stageListController.onItemSelected += self.onStageSelected

        self.functionSelectorController = FunctionSelectorController(self.view.functionSelectorView)
        self.functionSelectorController.onCodeInserted += self.onCodeInserted

    def createStageListController(self, view):
        """
        Create the associated list controller. Override in subclasses.
        """
        return StageListController(view)

    def setStage(self, stage):
        """
        Set the current stage and update the view contents.
        """
        self.currentStage = stage
        if stage is not None:
            self.updateView()

    def setStageList(self, stages):
        """
        Load a list of stages.
        """
        self.stages = stages
        self.stageListController.loadStages(stages)
        if stages:
            self.setStage(self.stages[0])

    def updateView(self):
        """
        Update the view content based on the current stage.
        """
        self.view.updateView(self.currentStage)

    def updateName(self, index):
        """
        Update the name of the stages at a certain index.
        """
        self.stages[index].loadFromData({"name": Stage.getNameFromIndex(index)})
        self.stageListController.setItemText(index, self.stageListController.getNameFromIndex(index))

    # ---------- Events ------------

    def onStageAdded(self, stage):
        """
        Called when a stage is created. Appends a new stage to the list.
        """
        if self.stages is None:
            return

        self.stages.append(stage)
        self.onStageSelected(len(self.stages) - 1)

    def onStageRemoved(self, index):
        """
        Called when a stage is removed.
        If necessary, update all stages name to always take into account their index.
        """
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
        """
        Called when a stage is selected.
        """
        self.stageListController.selectRow(index)
        if self.stages:
            self.setStage(self.stages[index])

    def onViewChanged(self, **kwargs):
        """
        Called when an element in the view has been modified. kwargs contains the change element and its value.
        """
        if self.currentStage is not None:
            self.currentStage.loadFromData(kwargs)

    def onCodeInserted(self, element, elementType):
        """
        Called when the user inserts an element (function or variable) in the stage code area
        """
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


# --------------------------

class StageListController(SingleItemListController):
    """
    Controller for a list of stage. See SingleItemListController.
    """
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

    def setCurrentText(self, text):
        self.setItemText(self.view.getCurrentIndex(), text)

    def loadStages(self, stages):
        """
        Creates every stage from stages to load
        """
        self.view.clear()
        for _ in stages:
            self.view.addItem(self.getDefaultName())


# --------------------------

class FunctionSelectorController:
    """
    Controller for the functions and variables to insert in stage code.
    """
    def __init__(self, view):
        self.view = view
        self.view.onInsert += self.onInsert
        self.view.onFunctionSelected += self.onFunctionSelected
        self.view.onVariableSelected += self.onVariableSelected
        self.view.onTabSelected += self.onTabSelected

        self.selection = None
        self.selectionType = None
        self.onCodeInserted = Event()

        self.functions = {}
        self.variables = []
        self.loadElements()
        self.setupView()

        self.updateView()

    def updateView(self):
        """
        Update the view contents depending on the current selection (function or variable).
        """
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
        """
        Adds all available functions and variables to the view.
        """
        for func in self.functions:
            self.view.addFunction(func["call"])
        for var in self.variables:
            self.view.addVariable(var["name"])

    # ---------- Events ------------

    def onInsert(self):
        """
        Called when the user click on the insertion button.
        """
        if self.selection is None:
            return
        self.onCodeInserted(self.selection, self.selectionType)

    def onFunctionSelected(self, index):
        """
        Called when a function has been selected. Update the view to display its description.
        """
        self.selection = self.functions[index]
        self.selectionType = "func"
        self.updateView()

    def onVariableSelected(self, index):
        """
        Called when a variable has been selected. Update the view to display its description.
        """
        self.selection = self.variables[index]
        self.selectionType = "var"
        self.updateView()

    def onTabSelected(self, index):
        if index == 0:
            self.onFunctionSelected(self.view.FunctionList.currentRow())
        elif index == 1:
            self.onVariableSelected(self.view.VariableList.currentRow())

    # --------------------------

    def loadElements(self):
        """
        Creates every function and variable from the model.
        """
        with ResourceLoader.openData("objective_model.json") as functionFile:
            modelData = json.load(functionFile)
            for func in modelData["functions"]:
                call = func["call"]
                if call in self.functions:
                    self.functions[call]["description"] += f'\n\nOverload {func["arguments"]} : {func["description"]}\nReturn : {func["return"]}'
                else:
                    self.functions[call] = func
                    self.functions[call]["description"] = f'Arguments {func["arguments"]} : {func["description"]}\nReturn : {func["return"]}'

            self.functions = list(self.functions.values())
            self.variables = modelData["variables"]
