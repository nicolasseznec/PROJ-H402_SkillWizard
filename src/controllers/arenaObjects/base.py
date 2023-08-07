from src.models.arenaObjects.base import BaseArenaObject
from src.util import Event, Shape, containsAny
from src.views.arenaObjects.base import BaseArenaObjectView, MultiArenaObjectView


class BaseArenaObjectController:
    def __init__(self, model: BaseArenaObject, view: BaseArenaObjectView):
        self.model = model
        self.view = view
        self.view.onItemChanged += self.onViewChanged

    def updateView(self):
        self.view.updateView(self.model)

    # ---------- Events ------------

    def onViewChanged(self, **kwargs):
        self.model.loadFromData(kwargs)

        dimensions = self.model.toJson()
        if containsAny(kwargs, "width", "height", "orientation"):
            self.view.updateShapes(Shape.Rectangle, **dimensions)
        if containsAny(kwargs, "radius"):
            self.view.updateShapes(Shape.Circle, **dimensions)


class MultiArenaObjectController(BaseArenaObjectController):
    def __init__(self, model, view: MultiArenaObjectView):
        super().__init__(model, view)
        self.view.onSelected += self.onViewSelected
        self.onSelected = Event()

    def handleRemoval(self):
        self.onSelected.clear()
        self.view.disconnectSettings()

    def setSelected(self, selected):
        self.view.setSelected(selected)

    # ---------- Events ------------

    def onViewSelected(self):
        self.onSelected(self)


# ------------ Item Lists --------------

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
        self.onItemAdded(item)

    def removeItem(self, index):
        self.view.removeItem(index)
        self.handleRemoval(self.itemsControllers.pop(index))
        self.onItemRemoved(index)

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


class ArenaListController(ItemListController):
    def unselectAll(self):
        for item in self.itemsControllers:
            item.setSelected(False)

    def setTabFocus(self, focus):
        for item in self.itemsControllers:
            item.setTabFocus(focus)

        index = self.view.getCurrentIndex()
        if focus and index >= 0:
            pass  # select item at current index

    def setArenaPath(self, arenaPath):
        pass

    def loadItems(self, items):
        for item in items:
            view = self.view.createNewItem()
            controller = self.createNewController(item, view)
            self.view.addItem(view, item.name)
            self.itemsControllers.append(controller)
            self.onItemAdded(item)

    def createNewController(self, model, view):
        controller = self.controllerFactory(model, view)
        controller.onSelected += self.onControllerSelected
        return controller

    def controllerFactory(self, model, view):
        pass

    def handleRemoval(self, controller):
        controller.onSelected -= self.onControllerSelected
        controller.handleRemoval()

    # ---------- Events ------------

    def onControllerSelected(self, controller):
        self.view.selectRow(self.itemsControllers.index(controller))

    def selectItem(self, index):
        self.onItemSelected(index)
        self.itemsControllers[index].setSelected(True)
