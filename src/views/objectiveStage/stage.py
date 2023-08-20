from PyQt5.QtWidgets import QWidget, QToolButton, QListWidget, QGroupBox

from src.util import Event, ResourceLoader
from src.views.utils.itemList import SingleItemListView


class StageView(QWidget):
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
        pass

    def createStageListView(self, container):
        return StageListView(container)

    def updateView(self, stage):
        self.blockSignals = True
        self.StageName.setText(f'<html><head/><body><p><span style=" font-size:11pt;">{stage.name}</span></p></body></html>')
        self.CodeArea.setPlainText(stage.code)
        self.blockSignals = False
        self.setEnabled(True)

    def clear(self):
        self.StageName.setText("")
        self.CodeArea.setPlainText("")
        self.setEnabled(False)

    def insertCode(self, code):
        cursor = self.CodeArea.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText(code)
        self.CodeArea.setFocus()

    # ---------- Events ------------

    def codeAreaChanged(self):
        self.onStageChanged(code=self.CodeArea.toPlainText())


# --------------------------

class StageListView(SingleItemListView):
    def __init__(self, settingsContainer):
        self.settingsContainer = settingsContainer
        addButton, removeButton, listWidget = self.getWidgets(settingsContainer)
        super().__init__(addButton, removeButton, listWidget)

    def getWidgets(self, settingsContainer):
        return QToolButton(), QToolButton(), QListWidget()


# --------------------------

class FunctionSelectorView(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        ResourceLoader.loadWidget("objective/FunctionSelector.ui", self)

        self.onInsert = Event()
        self.onFunctionSelected = Event()
        self.onVariableSelected = Event()

        self.InsertButton.clicked.connect(self.onInsertButtonClicked)
        self.FunctionList.currentRowChanged.connect(self.onFunctionChanged)
        self.VariableList.currentRowChanged.connect(self.onVariableChanged)

    def updateView(self, name, description):
        self.SelectionName.setText(f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{name}</span></p></body></html>')
        self.SelectionDescription.setText(description)

    # ---------- Events ------------

    def onInsertButtonClicked(self):
        self.onInsert()

    def onFunctionChanged(self, index):
        self.onFunctionSelected(index)

    def onVariableChanged(self, index):
        self.onVariableSelected(index)

    # --------------------------

    def addFunction(self, name):
        self.FunctionList.addItem(name)

    def addVariable(self, name):
        self.VariableList.addItem(name)
