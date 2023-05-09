from PyQt5.QtWidgets import QListWidget, QToolButton, QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton

from src.util import Event


class ItemList:
    def __init__(self, container=None):
        self.items = []
        self.onItemRemoved = Event()
        self.onItemSelected = Event()
        self.onItemAdded = Event()
        self.container = None

        if container is not None:
            self.connectWidgets(container)

    def onAdd(self):
        self.listWidget.addItem(self.getDefaultName())
        item = self.createNewItem()
        self.items.append(item)
        self.onItemAdded(item)
        self.listWidget.setCurrentRow(self.listWidget.count()-1)

    def onRemove(self):
        index = self.listWidget.currentRow()
        if index < 0 or index >= len(self.items):
            return
        self.listWidget.takeItem(index)
        item = self.items.pop(index)
        self.onItemRemoved(item)
        self.handleRemoval(item)

    def getDefaultName(self):
        return "New Item"

    def onSelectedChanged(self, index):
        self.onItemSelected(self.items[index])

    def createNewItem(self):
        return None

    def handleRemoval(self, item):
        pass

    def connectWidgets(self, container):
        self.container = container
        self.getWidgets(container)
        self.listWidget.currentRowChanged.connect(self.onSelectedChanged)
        self.listWidget.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.addButton.clicked.connect(self.onAdd)
        self.removeButton.clicked.connect(self.onRemove)

    def getWidgets(self, container):
        self.listWidget = QListWidget()
        self.addButton = QToolButton()
        self.removeButton = QToolButton()

    def onItemDoubleClicked(self, item):
        pass


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
