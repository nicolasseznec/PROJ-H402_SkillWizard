from src.util import Event


class ItemListController:
    def __init__(self, view):
        self.itemsControllers = []

        self.view = view

        self.onItemAdded = Event()
        self.onItemRemoved = Event()
        # self.onItemSelected = Event()

        self.view.onItemAdded += self.addItem
        self.view.onItemRemoved += self.removeItem
        # self.view.onItemSelected += self.onItemSelected

    # ----------------------

    def addItem(self):
        item = self.createNewItem()
        view = self.view.createNewItem()
        controller = self.createNewController(item, view)
        self.view.addItem(view, self.getDefaultName())
        self.itemsControllers.append(controller)
        self.onItemAdded(item)

    def removeItem(self, index):
        self.view.removeItem(index)
        self.itemsControllers.pop(index)
        self.onItemRemoved(index)

    # def selectItem(self, index):
    #     pass

    # ------------------------------

    def getDefaultName(self):
        return "New Item"

    def createNewController(self, model, view):
        pass

    def createNewItem(self):
        pass


class ArenaListController(ItemListController):
    pass
