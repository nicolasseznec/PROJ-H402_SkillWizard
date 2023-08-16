from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton

from src.util import Event


class SingleItemListView:
    def __init__(self, addButton, removeButton, listWidget):
        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemSelected = Event()
        self.onItemDoubleClicked = Event()

        self.listWidget = listWidget
        self.addButton = addButton
        self.removeButton = removeButton
        self.connectWidgets()

    def connectWidgets(self):
        self.listWidget.currentRowChanged.connect(self.onSelectedChanged)
        self.listWidget.itemDoubleClicked.connect(self.onDoubleClick)
        self.addButton.clicked.connect(self.onAdd)
        self.removeButton.clicked.connect(self.onRemove)

    def getCurrentIndex(self):
        return self.listWidget.currentRow()

    def selectRow(self, index):
        self.listWidget.blockSignals(True)
        self.listWidget.setCurrentRow(index, QItemSelectionModel.ClearAndSelect)
        self.listWidget.blockSignals(False)

    def setItemText(self, index, text):
        self.listWidget.item(index).setText(text)

    def count(self):
        return self.listWidget.count()

    # ---------- Events ------------

    def onAdd(self):
        self.onItemAdded()

    def onRemove(self):
        self.onItemRemoved(self.listWidget.currentRow())

    def onSelectedChanged(self, index):
        self.onItemSelected(index)

    def onDoubleClick(self, item):
        self.onItemDoubleClicked(self.listWidget.row(item))

    # ----------- Add/Remove -------------

    def addItem(self, name="New Item"):
        self.listWidget.addItem(name)

    def removeItem(self, index):
        self.listWidget.takeItem(index)

    # -------------------------------------

    def clear(self):
        self.listWidget.blockSignals(True)
        self.listWidget.clear()
        self.listWidget.blockSignals(False)


class ItemListView:
    def __init__(self, addButton, removeButton, listWidget):
        self.items = []

        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemSelected = Event()
        self.onItemDoubleClicked = Event()

        self.listWidget = listWidget
        self.addButton = addButton
        self.removeButton = removeButton
        self.connectWidgets()

    def connectWidgets(self):
        self.listWidget.currentRowChanged.connect(self.onSelectedChanged)
        self.listWidget.itemDoubleClicked.connect(self.onDoubleClick)
        self.addButton.clicked.connect(self.onAdd)
        self.removeButton.clicked.connect(self.onRemove)

    def createNewItem(self):
        return None

    def getItem(self, index):
        return self.items[index]

    def getCurrentIndex(self):
        return self.listWidget.currentRow()

    def selectRow(self, index):
        self.listWidget.blockSignals(True)
        self.listWidget.setCurrentRow(index)
        self.listWidget.blockSignals(False)

    def setItemText(self, index, text):
        self.listWidget.item(index).setText(text)

    # ---------- Events ------------

    def onAdd(self):
        self.onItemAdded()

    def onRemove(self):
        index = self.listWidget.currentRow()
        if index < 0 or index >= len(self.items):
            return
        self.onItemRemoved(index)

    def onSelectedChanged(self, index):
        self.onItemSelected(index)

    def onDoubleClick(self, item):
        self.onItemDoubleClicked(self.listWidget.row(item))

    # ----------- Add/Remove -------------

    def addItem(self, item, name="New Item"):
        self.listWidget.addItem(name)
        self.items.append(item)

    def removeItem(self, index):
        self.listWidget.takeItem(index)
        self.items.pop(index)

    # -------------------------------------

    def clear(self):
        self.listWidget.blockSignals(True)
        self.listWidget.clear()
        self.listWidget.blockSignals(False)
        self.items.clear()


class TextDialog(QDialog):
    def __init__(self, parent=None, initialText='', dialogName=''):
        super().__init__(parent)
        if dialogName:
            self.setWindowTitle(dialogName)
        self.setLayout(QVBoxLayout())

        lineEdit = QLineEdit()
        if initialText:
            lineEdit.setText(initialText)
            lineEdit.selectAll()
        self.layout().addWidget(lineEdit)

        buttons_layout = QHBoxLayout()
        self.layout().addLayout(buttons_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def getLineEditValue(self):
        return self.layout().itemAt(0).widget().text()

    def getNewText(self):
        if self.exec_() == QDialog.Accepted:
            return self.getLineEditValue()
