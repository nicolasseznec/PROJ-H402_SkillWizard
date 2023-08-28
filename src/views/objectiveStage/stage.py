from PyQt5.QtWidgets import QWidget, QToolButton, QListWidget, QGroupBox

from src.util import Event, ResourceLoader
from src.views.utils.itemList import SingleItemListView


class StageView(QWidget):
    """
    View for the objective's stages.
    """
    def __init__(self, container, *__args):
        super().__init__(*__args)
        self.loadWidget()
        self.stageListView = self.createStageListView(container)

        self.functionSelectorView = FunctionSelectorView()
        self.layout().addWidget(self.functionSelectorView)

        self.onStageChanged = Event()
        self.CodeArea.textChanged.connect(self.codeAreaChanged)

        self.clear()
        self.blockSignals = False

    def loadWidget(self):
        """
        Load the widget for this view. Override in subclasses.
        """
        pass

    def createStageListView(self, container):
        """
        Create the associated list controller. Override in subclasses.
        """
        return StageListView(container)

    def updateView(self, stage):
        """
        Update the view content based on the given stage.
        """
        self.blockSignals = True
        self.StageName.setText(f'<html><head/><body><p><span style=" font-size:11pt;">{stage.name}</span></p></body></html>')
        self.CodeArea.setPlainText(stage.code)
        self.blockSignals = False
        self.setEnabled(True)

    def clear(self):
        """
        Clear the view content and disable the interface.
        """
        self.StageName.setText("")
        self.CodeArea.setPlainText("")
        self.setEnabled(False)

    def insertCode(self, code):
        """
        Insert the given code in the code area.
        """
        cursor = self.CodeArea.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText(code)
        self.CodeArea.setFocus()

    # ---------- Events ------------

    def codeAreaChanged(self):
        """
        Called when the code area has been modified.
        """
        self.onStageChanged(code=self.CodeArea.toPlainText())


# --------------------------

class StageListView(SingleItemListView):
    """
    View for a list of stage. See SingleItemListView
    """
    def __init__(self, settingsContainer):
        self.settingsContainer = settingsContainer
        addButton, removeButton, listWidget = self.getWidgets(settingsContainer)
        super().__init__(addButton, removeButton, listWidget)

    def getWidgets(self, settingsContainer):
        return QToolButton(), QToolButton(), QListWidget()


# --------------------------

class FunctionSelectorView(QGroupBox):
    """
    View for the functions and variables to insert in stage code.
    """
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("objective/FunctionSelector.ui", self)

        self.onInsert = Event()
        self.onFunctionSelected = Event()
        self.onVariableSelected = Event()
        self.onTabSelected = Event()

        self.InsertButton.clicked.connect(self.onInsertButtonClicked)
        self.FunctionList.currentRowChanged.connect(self.onFunctionChanged)
        self.VariableList.currentRowChanged.connect(self.onVariableChanged)
        self.Tabs.currentChanged.connect(self.onTabChanged)

    def updateView(self, name, description):
        self.SelectionName.setText(f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{name}</span></p></body></html>')
        self.SelectionDescription.setText(description)

    # ---------- Events ------------

    def onInsertButtonClicked(self):
        """
        Called when the user click on the insertion button.
        """
        self.onInsert()

    def onFunctionChanged(self, index):
        """
        Called when a function has been selected. Update the view to display its description.
        """
        self.onFunctionSelected(index)

    def onVariableChanged(self, index):
        """
        Called when a variable has been selected. Update the view to display its description.
        """
        self.onVariableSelected(index)

    def onTabChanged(self, index):
        self.onTabSelected(index)

    # --------------------------

    def addFunction(self, name):
        """
        Adds a function to the functions list
        """
        self.FunctionList.addItem(name)

    def addVariable(self, name):
        """
        Adds a variable to the variables list
        """
        self.VariableList.addItem(name)
