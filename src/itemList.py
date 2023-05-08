from PyQt5.QtWidgets import QListWidget, QToolButton

from src.util import Event


class ItemList:
    def __init__(self, container=None):
        self.items = []
        self.onItemRemoved = Event()
        self.onItemSelected = Event()
        self.onItemAdded = Event()

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
        print(index)
        self.onItemSelected(self.items[index])

    def createNewItem(self):
        return None

    def handleRemoval(self, item):
        pass

    def connectWidgets(self, container):
        self.getWidgets(container)
        self.listWidget.currentRowChanged.connect(self.onSelectedChanged)
        self.addButton.clicked.connect(self.onAdd)
        self.removeButton.clicked.connect(self.onRemove)

    def getWidgets(self, container):
        self.listWidget = QListWidget()
        self.addButton = QToolButton()
        self.removeButton = QToolButton()
