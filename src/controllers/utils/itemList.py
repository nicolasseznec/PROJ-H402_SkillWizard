from src.util import Event


class SingleItemListController:
    def __init__(self, view):
        self.view = view

        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemSelected = Event()

        self.view.onItemAdded += self.addItem
        self.view.onItemRemoved += self.removeItem
        self.view.onItemSelected += self.onItemSelected
        self.view.onItemDoubleClicked += self.onItemDoubleClicked

    # ----------------------

    def addItem(self):
        item = self.createNewItem()
        self.view.addItem(self.getDefaultName())
        self.onItemAdded(item)

    def removeItem(self, index):
        self.view.removeItem(index)
        self.onItemRemoved(index)

    def onItemDoubleClicked(self, index):
        pass

    # ------------------------------

    def getDefaultName(self):
        return "New Item"

    def createNewItem(self):
        pass

    def clear(self):
        self.view.clear()


class ItemListController:
    def __init__(self, view):
        self.itemsControllers = []

        self.view = view

        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        self.onItemSelected = Event()

        self.view.onItemAdded += self.addItem
        self.view.onItemRemoved += self.removeItem
        self.view.onItemSelected += self.selectItem
        self.view.onItemDoubleClicked += self.onItemDoubleClicked

    # ----------------------

    def addItem(self):
        item = self.createNewItem()
        view = self.view.createNewItem()
        controller = self.createNewController(item, view)
        self.view.addItem(view, self.getDefaultName())
        self.itemsControllers.append(controller)
        self.onItemAdded(controller)

    def removeItem(self, index):
        self.view.removeItem(index)
        controller = self.itemsControllers.pop(index)
        self.handleRemoval(controller)
        self.onItemRemoved(controller)

    def selectItem(self, index):
        pass

    def onItemDoubleClicked(self, index):
        controller = self.itemsControllers[index]
        dialog = self.view.getTextDialog(index)
        text = dialog.getNewText()
        if text:
            self.view.setItemText(index, text)
            controller.setName(text)

    # ------------------------------

    def getDefaultName(self):
        return "New Item"

    def createNewController(self, model, view):
        pass

    def createNewItem(self):
        pass

    def handleRemoval(self, controller):
        pass

    def clear(self):
        for item in self.itemsControllers:
            item.handleRemoval()
        self.view.clear()
        self.itemsControllers.clear()
